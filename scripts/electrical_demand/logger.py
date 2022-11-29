import logging

def get_logger(name, level="ERROR"):
    """
    Function to get a Python logger. It can be used for different objects to share the same logger.

    Parameters
    ----------
    name : str
        logger file name
    leve : str, optional
        debugger level

    Returns
    -------
    logger : python logger
        Return a python logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    formatter = logging.Formatter("%(asctime)s:%(levelname)s:%(name)s:%(message)s")
    file_handler = logging.FileHandler("logging.log")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger