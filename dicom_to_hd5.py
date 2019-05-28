#!/usr/bin/env python3
"""
Main file for running the application
"""

import argparse
from pathlib import Path
import config
import logging
from pydicom.filereader import dcmread
import numpy as np
import h5py

def existing_path(path):
    path = Path(path)

    if not path.exists():
        raise argparse.ArgumentTypeError('file/directory doesn\'t exist')

    if path.is_file() and not path.suffix.lower() in config.SUPPORTED_IMG_EXTN:
        raise argparse.ArgumentTypeError('The only supported extensions are: ' + str(config.SUPPORTED_IMG_EXTN))

    return path

def get_logger():
    logger = logging.getLogger(config.APP_NAME)
    logger.setLevel(config.APP_LOG_LEVEL)
    hdlr = logging.FileHandler(config.APP_LOG_FILE)
    logger.addHandler(hdlr)
    logger.propagate = False
    return logger

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
    volume = volume.astype(np.float32)
    print(volume.shape, len(dcms))


    print(set(map(lambda x: x.Modality, dcms[:15])))
    print(set(map(lambda x: x.SeriesInstanceUID, dcms[:15])))

    print(set(map(lambda x: x.SOPInstanceUID, dcms[:15])))
    return None



if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Convert DICOMs to HD5 and JSON', add_help=False)
    parser.add_argument('--input-dicom', '-i', required=True, type=existing_path, help='Directory with DICOMs and JSON')
    parser.add_argument('--output-hdf5', '-h', required=True, help='Path to output HD5')
    parser.add_argument('--output-json', '-j', required=True, help='Path to output JSON')
    args = parser.parse_args()

    logger = get_logger()
    logger.info("App Log initiated")

    logger.info("Retrieving DICOMS")
    dcms = get_dcms(args.input_dicom)
    logger.info("Got %d DICOMS" % len(dcms))

    logger.info("Constructing 3D Volume")
    volume = construct_volume(dcms)
    print()

