import numpy as np
import dicom_to_hd5
import hd5_to_dicom
import pathlib


def convolve_3d(input_3d, kernel_1d, pad_size, convolve_dim, output_shape):
    """
    Do 3D convolution by series of 1d convolutions

    :param input_3d:
    :param kernel_1d:  Kernel to convolve by
    :param pad_size:  Amount to pad the input by
    :param convolve_dim: Dimension to convolve on
    :param output_shape: Expected Output shape
    :return:
    """

    # Re-order dimensions for iteration for 3d input
    dims = [0, 1, 2]
    dims.remove(convolve_dim)

    # Output array, constaint to the original input
    conv = np.zeros(output_shape)
    kernel_size = len(kernel_1d)

    # Pad the input
    padding = [[0,], [0,], [0,]]
    padding[convolve_dim][0] = pad_size
    padded_input = np.pad(input_3d, padding, 'edge')

    # Perform 1d convolution
    for i in range(output_shape[dims[0]]):
        for j in range(output_shape[dims[1]]):
            for k in range(output_shape[convolve_dim]):
                if convolve_dim == 0:
                    conv[k, i, j] = np.convolve(kernel_1d, padded_input[k:k + kernel_size, i, j], 'valid')
                elif convolve_dim == 1:
                    conv[i, k, j] = np.convolve(kernel_1d, padded_input[i, k:k + kernel_size, j], 'valid')
                else:
                    conv[i, j, k] = np.convolve(kernel_1d, padded_input[i, j, k:k + kernel_size], 'valid')

    return conv

def gauss_kernel(sigma, spread):
    gauss = np.exp((-1 / (2 * sigma ** 2)) * np.arange(-spread, spread + 1) ** 2)
    return gauss / np.sum(gauss)

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

    img_shape = input_3d.shape
    dim_count = len(img_shape)

    # Calculate relative sigma values for each dim
    sigma = [config['sigma'] / meta_data['spacing'][i] for i in range(dim_count)]

    # Calculate kernel spread for each dim
    kernel_spread  = [int(np.round(dim_count * sigma_i)) for sigma_i in sigma]

    # Create Gaussian Kernel for each dim
    kernels = [gauss_kernel(sigma_i, spread_i) for sigma_i, spread_i in zip(sigma, kernel_spread)]

    # Convolve around each dimnesion
    output = input_3d
    for i in range(dim_count):
        output = convolve_3d(output, kernels[i], kernel_spread[i], i, img_shape)

    return output


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

