import logging
import time
import os

"""
Levels:

DEBUG: Detailed information, typically of interest only when diagnosing problems.
logging.debug

INFO: Confirmation that things are working as expected. 
logging.info

WARNING: An indication that something unexpected happened, or indicative of some problem in the near future (e.g. disk space low). 
logging.warning

ERROR: Due to a more serious problem, the software has not been able to perform some function. 
logging.error

CRITICAL: A serious error, indicating that the program itself may be unable to continue running. 
logging.critical
"""


class CustomFormatter(logging.Formatter):

    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = '%(asctime)s [%(levelname)s] - "%(pathname)s", line %(lineno)d, %(funcName)s - %(message)s'

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def setup_logger():
    # Ensure the log directory exists
    os.makedirs("logs", exist_ok=True)

    # Create a logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # Create console handler
    consoleHandler = logging.StreamHandler()
    consoleHandler.setLevel(logging.DEBUG)
    consoleHandler.setFormatter(CustomFormatter())

    # Create file handler
    fileHandler = logging.FileHandler(f'{time.strftime("logs/%Y%m%d_%H%M%S")}.log')
    fileHandler.setLevel(logging.DEBUG)
    fileHandler.setFormatter(logging.Formatter(CustomFormatter.format))

    # Add handlers to the logger
    if not logger.hasHandlers():
        logger.addHandler(consoleHandler)
        logger.addHandler(fileHandler)

    return logger


logger = setup_logger()
