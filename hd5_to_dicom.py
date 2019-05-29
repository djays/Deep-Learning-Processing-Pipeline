#!/usr/bin/env python3
"""
Main file for running the application
"""

import argparse
import config
import utils
from pydicom.filereader import dcmread
from pydicom.uid import generate_uid
import numpy as np
import h5py
import json
import os

def construct_volume(dcms):
    """ Construct 3D volume from the dicoms, slices arranged by slice location.
        Output Volume is normalized and in range of [0,1]
    """

    # Sort by slice location
    dcms = sorted(dcms, key = lambda dcm: float(dcm.SliceLocation))

    # Construct 3D volume
    volume = np.stack(list(map(lambda dcm: dcm.pixel_array, dcms)))

    # Normalize Volume
    volume = (volume - np.min(volume)) / (np.max(volume) - np.min(volume))

    return volume.astype(np.float32)


def extract_attributes(dcms):
    """Extract Desired attributes from dicom to json"""
    return { config.DCM_TO_JSON_MAP[dcm_attrib] : dcms[0].get(dcm_attrib, None)
             for dcm_attrib in config.DCM_TO_JSON_MAP}


def save_dcms(volume, attribs, path_hdf5, path_json):
    """ Save volume and Attributes to HDF5 and JSON"""
    logger.info("Saving Volume to HDF5 %s" % (path_hdf5,))

    volume_file = h5py.File(path_hdf5, "w")
    volume_file.create_dataset("data", data=volume, dtype=np.float32)
    volume_file.close()

    logger.info("Converting and Saving JSON to %s" % (path_json, ))

    # Map DICOM types to JSON compatible format
    for key, val in attribs.items():
        type_val = type(val)
        if type_val in config.DCM_TYPE_TO_JSON_MAP:
            attribs[key] = config.DCM_TYPE_TO_JSON_MAP[type_val](val)

    # Write the JSON
    with open(path_json, 'w') as json_file:
        json.dump(attribs, json_file)

def read_hdf5_dataset(path):
    logger.info("Reading HDF5 at %s" % str(path))
    h5_file = h5py.File(str(path), "r")
    data = np.array(h5_file[config.HD5_DATASET_NAME])
    h5_file.close()
    return data

def split_volume_to_dcms(volume, template_dcms):

    # Verify shape
    if len(template_dcms) != volume.shape[0]:
        raise Exception("Number of template DCMS don't equal number of slices of 3d volume ")

    # Sort the template dcms to match the volume Slice Location
    ##TODO: Not mentioned but from the wording it appears that slice location doesnt have to be respected
    #template_dcms = sorted(template_dcms, key=lambda dcm: float(dcm.SliceLocation))

    # Generate UIDs
    series_iud =  generate_uid()

    # Copy back the pixel data
    for i, dcm in enumerate(template_dcms):

        a_slice = volume[i].squeeze()
        # Establish Scale range and  normalize to 0 and 1
        type_info = np.iinfo(dcm.pixel_array.dtype)
        a_slice = (a_slice - np.min(a_slice))/np.ptp(a_slice)
        # Prevent over/underflow,
        a_slice = a_slice.astype(np.float64)
        a_slice = a_slice * (type_info.max - type_info.min) + type_info.min
        a_slice = a_slice.astype(dcm.pixel_array.dtype)

        # Update Template
        dcm.PixelData = a_slice.tobytes()
        dcm.SeriesInstanceUID = series_iud
        dcm.SOPInstanceUID = generate_uid()


def app(input_hdf5, input_dicom, output_dicom, logger):
    """ Export pixel data from hdf5 to DICOMs images based on template DICOMs.

    Parameters
    --------
    input_hdf5: pathlib.Path
            Path to a 3D volume
    input_dicom: pathlib.Path
            Path to a/many template DICOMs
    output_dicom: str
            Path to output DICOM directory

    """

    logger.info("Retrieving DICOMS")
    dcm_paths = utils.get_files(input_dicom, config.DCM2HD5_INPUT_EXT)
    dcms = [dcmread(str(path)) for path in dcm_paths]

    logger.info("Got %d DICOMS" % len(dcms))

    volume = read_hdf5_dataset(input_hdf5)

    logger.info("Spliting 3D Volume to dcms")
    split_volume_to_dcms(volume, dcms)

    logger.info("Writing DICOMs to files")
    if not os.path.exists(output_dicom):
        logger.info("Creating output dir: %s" %(output_dicom,))
        os.mkdir(output_dicom)

    for i, dcm in enumerate(dcms):
        dcm_name = dcm_paths[i].name
        dcm.save_as(os.path.join(output_dicom, dcm_name))


if __name__ == '__main__':

    # Parse Arguments
    parser = argparse.ArgumentParser(description='Extract HD5 data to DICOM using template DICOM', add_help=False)
    parser.add_argument('--input-hdf5', '-h', required=True, type=utils.existing_path(config.HD5_INPUT_EXT), help='Path to input HD5')
    parser.add_argument('--input-dicom', '-d', required=True, type=utils.existing_path(config.DCM2HD5_INPUT_EXT), help='Path to the template DICOM directory')
    parser.add_argument('--output-dicom', '-o', required=True, help='Path to output DICOM directory')
    args = parser.parse_args()

    # App Specific Logger
    logger = utils.init_logger('H2D')

    # Main app logic
    app(args.input_hdf5, args.input_dicom, args.output_dicom, logger)








