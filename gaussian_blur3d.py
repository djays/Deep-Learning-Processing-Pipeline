import numpy as np
import dicom_to_hd5
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
    pass

def pre_gaussian_blur3d(input_dir:str, config: dict):
    """

    :param input_dir: String path of the input directory
    :param config: the dict to be passed to the main
    :return:
    """
    return dicom_to_hd5.app(pathlib.Path(input_dir), save_records = False) +  (config,)

