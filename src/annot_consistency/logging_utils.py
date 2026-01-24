import logging

def logger(log_file: str) -> logging.logger:
    logger = logging.getLogger("gffACAKE")
    logger.setLevel(logging.DEBUG)                                              # Set level to Debug
    logger.handlers.clear()                                                     # prevent duplicate logs if rerun
    format = logging.Formatter("%(levelname)s\t%(asctime)s\t%(message)s")       # logger output message
    filehandler = logging.FileHandler(log_file)
    filehandler.setLevel(logging.Debug)
    filehandler.setFormatter(format)
    logger.addHandler(format)
    return logger