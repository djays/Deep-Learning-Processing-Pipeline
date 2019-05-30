import logging
import pydicom

APP_NAME='subtle'
APP_LOG_FILE = 'debug.log'
APP_LOG_LEVEL = logging.DEBUG

DCM_TO_JSON_MAP = {'SpacingBetweenSlices' : 'spacing_slices', 'PixelSpacing': 'spacing_pixel' , 'Modality': 'modality'}
DCM_TYPE_TO_JSON_MAP = {pydicom.valuerep.DSfloat : float, pydicom.multival.MultiValue: list}

DCM2HD5_INPUT_EXT = ('.dcm', '.DCM')
HD5_INPUT_EXT = ('.hd5', '.HD5')

HD5_DATASET_NAME = 'data'
FILE_NAME_SEP = '_'
OUTPUT_FORMAT = '%s\t%d'

