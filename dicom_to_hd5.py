#!/usr/bin/env python3
"""
Main file for running the application
"""

import argparse
import config
import utils
from pydicom.filereader import dcmread
import numpy as np
import h5py
import json
import logging


def construct_volume(dcms):
    """ Construct 3D volume from the dicoms, slices arranged by slice location.
        Output Volume is normalized and in range of [0,1]
    """

    # Sort by slice location
    dcms = sorted(dcms, key=lambda dcm: float(dcm.SliceLocation))

    # Construct 3D volume
    volume = np.stack(list(map(lambda dcm: dcm.pixel_array, dcms)))

    # Normalize Volume
    volume = (volume - np.min(volume)) / (np.max(volume) - np.min(volume))

    return volume.astype(np.float32)


def extract_attributes(dcms):
    """Extract Desired attributes from dicom to json"""
    return {config.DCM_TO_JSON_MAP[dcm_attrib]: dcms[0].get(dcm_attrib, None)
            for dcm_attrib in config.DCM_TO_JSON_MAP}


def save_record(volume, attribs, path_hdf5, path_json):
    """ Save volume and Attributes to HDF5 and JSON"""
    logger.info("Saving Volume to HDF5 %s" % (path_hdf5,))

    volume_file = h5py.File(path_hdf5, "w")
    volume_file.create_dataset(config.HD5_DATASET_NAME, data=volume, dtype=np.float32)
    volume_file.close()

    logger.info("Converting and Saving JSON to %s" % (path_json,))

    # Map DICOM types to JSON compatible format
    for key, val in attribs.items():
        type_val = type(val)
        if type_val in config.DCM_TYPE_TO_JSON_MAP:
            attribs[key] = config.DCM_TYPE_TO_JSON_MAP[type_val](val)

    # Write the JSON
    with open(path_json, 'w') as json_file:
        json.dump(attribs, json_file)


def app(input_dicom, output_hdf5 = None , output_json = None, save_records = True):
    """ Construct a 3D volume from the dicoms present in the path and
    save the pixel data to a HDf5 and attributes to a json.

    Parameters
    --------
    input_dicom: Path
            Path to a/many DICOMs
    output_hdf5: str
            Path to create output HDF5
    output_json:
            Path to create output JSON

    """

    logger = logging.getLogger(config.APP_NAME)
    logger.info("Retrieving DICOMS")
    dcm_paths = utils.get_files(input_dicom, config.DCM2HD5_INPUT_EXT)
    dcms = [dcmread(str(path)) for path in dcm_paths]
    logger.info("Got %d DICOMS" % len(dcms))

    logger.info("Constructing 3D Volume")
    volume = construct_volume(dcms)

    logger.info("Extracting Attributes")
    attributes = extract_attributes(dcms)

    if save_records:
        save_record(volume, attributes, output_hdf5, output_json)

    return volume, attributes


if __name__ == '__main__':
    # Parse Arguments
    parser = argparse.ArgumentParser(description='Convert DICOMs to HD5 and JSON', add_help=False)
    parser.add_argument('--input-dicom', '-i', required=True, type=utils.existing_path(config.DCM2HD5_INPUT_EXT),
                        help='Path to DICOM/s')
    parser.add_argument('--output-hdf5', '-h', required=True, help='Path to output HD5')
    parser.add_argument('--output-json', '-j', required=True, help='Path to output JSON')
    args = parser.parse_args()

    # App Specific Logger
    logger = utils.init_logger()

    # Main app logic
    app(args.input_dicom, args.output_hdf5, args.output_json)