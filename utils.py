import config
import logging
from pathlib import Path
import argparse

def init_logger(app_postfix):
    """ Initialize the application level logger.
    Parameters
    --------
    app_postfix: str
            Logger name postfix

    """
    logger = logging.getLogger(config.APP_NAME + '_' + app_postfix)
    logger.setLevel(config.APP_LOG_LEVEL)
    hdlr = logging.FileHandler(config.APP_LOG_FILE)
    logger.addHandler(hdlr)
    logger.propagate = False
    logger.info("App Log initiated")
    return logger


def existing_path(supported_extn, expects_single_file=False):
    """ Existing Path Check Type for ArgParse.

    Parameters
    --------
    supported_extn: Collection
            Collection of supported extensions
    expects_single_file: bool
            If the expected path points to a single file.
    """
    def inner_validation(path):
        path = Path(path)

        if not path.exists():
            raise argparse.ArgumentTypeError('file/directory doesn\'t exist: %s' % (path,))

        elif path.is_file() and not path.suffix.lower() in supported_extn:
            raise argparse.ArgumentTypeError('The only supported extensions are: ' + str(supported_extn))

        elif expects_single_file and not path.is_file():
            raise argparse.ArgumentTypeError('Expected a single file at path: %s' % (path, ))

        return path

    return inner_validation

def get_files(path, supported_extn):
    """Get all files present in path

    Parameters
    --------
    path: pathlib.Path
            Input path
    supported_extn: Collection
            Collection of supported extensions.

    """

    # If it's a directory, scan for all supported extension and flatten the final list

    if path.is_dir():
        file_list = [list(path.glob('**/*' + extn)) for extn in supported_extn]
        file_list = [f for a_list in file_list for f in a_list]
    else:
        file_list = [path]

    return file_list