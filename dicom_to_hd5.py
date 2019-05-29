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
from pathlib import Path



def get_dcms(path):
    """Get all dcms present in path"""
    # If it's a directory, scan for all supported extension and flatten the final list

    if path.is_dir():
        img_list = [list(path.glob('**/*' + extn)) for extn in config.SUPPORTED_IMG_EXTN]
        img_list = [ f for a_list in img_list for f in a_list ]
    else:
        img_list = [path]

    return [dcmread(str(img)) for img in img_list]

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


def save_record(volume, attribs, path_hdf5, path_json):
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


def existing_path(path):
    path = Path(path)

    if not path.exists():
        raise argparse.ArgumentTypeError('file/directory doesn\'t exist')

    if path.is_file() and not path.suffix.lower() in config.SUPPORTED_IMG_EXTN:
        raise argparse.ArgumentTypeError('The only supported extensions are: ' + str(config.SUPPORTED_IMG_EXTN))

    return path

if __name__ == '__main__':

    # Parse Arguments
    parser = argparse.ArgumentParser(description='Convert DICOMs to HD5 and JSON', add_help=False)
    parser.add_argument('--input-dicom', '-i', required=True, type=existing_path, help='Path to DICOM/s')
    parser.add_argument('--output-hdf5', '-h', required=True, help='Path to output HD5')
    parser.add_argument('--output-json', '-j', required=True, help='Path to output JSON')
    args = parser.parse_args()

    logger = utils.init_logger()
    logger.info("App Log initiated")

    logger.info("Retrieving DICOMS")
    dcms = get_dcms(args.input_dicom)
    logger.info("Got %d DICOMS" % len(dcms))

    logger.info("Constructing 3D Volume")
    volume = construct_volume(dcms)

    logger.info("Extracting Attributes")
    attributes = extract_attributes(dcms)

    save_record(volume, attributes, args.output_hdf5, args.output_json)





