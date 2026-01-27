import logging

def logger(log_file: str) -> logging.Logger:
    logger = logging.getLogger("gffACAKE")
    logger.setLevel(logging.DEBUG)      # Set level to Debug; capture everything
    if logger.handlers:                                           
        logger.handlers.clear()     # prevent duplicate logs if rerun
    format = logging.Formatter("%(levelname)s\t%(asctime)s\t%(message)s")       # logger output message
    filehandler = logging.FileHandler(log_file)
    filehandler.setLevel(logging.DEBUG)
    filehandler.setFormatter(format)
    logger.addHandler(filehandler)
    logger.propagate = False        # Prevent log records from propagating to parent loggers.
    return logger

