import logging
import pydicom

APP_NAME='subtle'
APP_LOG_FILE = 'debug.log'
APP_LOG_LEVEL = logging.DEBUG
SUPPORTED_IMG_EXTN = ('.dcm', '.DCM')
FILE_NAME_SEP = '_'
OUTPUT_FORMAT = '%s\t%d'
DCM_TO_JSON_MAP = {'SpacingBetweenSlices' : 'spacing_slices', 'PixelSpacing': 'spacing_pixel' , 'Modality': 'modality'}
DCM_TYPE_TO_JSON_MAP = {pydicom.valuerep.DSfloat : float, pydicom.multival.MultiValue: list}