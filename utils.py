import config
import logging


def init_logger():
    """ Initialize the logger"""
    logger = logging.getLogger(config.APP_NAME)
    logger.setLevel(config.APP_LOG_LEVEL)
    hdlr = logging.FileHandler(config.APP_LOG_FILE)
    logger.addHandler(hdlr)
    logger.propagate = False
    return logger


