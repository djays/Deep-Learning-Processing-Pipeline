import numpy as np
import dicom_to_hd5
import hd5_to_dicom
import pathlib

def gaussian_blur3d(input_3d: np.ndarray, meta_data: dict,
                    config: dict) -> np.array:
    '''Performs 3D Gaussian blur on the input volume

    :param input_3d: input volume in 3D numpy array
    :param meta_data: a dict object with the following key(s):
        'spacing': 3-tuple of floats, the pixel spacing in 3D
    :param config: a dict object with the following key(s):
        'sigma': a float indicating size of the Gaussian kernel

    :return: the blurred volume in 3D numpy array, same size as input_3d
    '''
    print(input_3d.shape, meta_data, config)
    return input_3d

def pre_gaussian_blur3d(input_dir:str, config: dict):
    """

    :param input_dir: String path of the input directory
    :param config: the dict to be passed to the main
    :return:
    """
    volume, attribs = dicom_to_hd5.dicom_to_hd5(pathlib.Path(input_dir), save_records = False)
    return  volume, attribs, config

def post_gaussian_blur3d(input_dir:str, output_dir:str, output_3d: np.ndarray):
    """

    :param output_dir: Directory to write the dicom
    :param input_3d:
    :return:
    """
    hd5_to_dicom.hd5_to_dicom(output_3d, pathlib.Path(input_dir), output_dir)

