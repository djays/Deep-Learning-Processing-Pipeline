import numpy as np


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
