import logging


def logger(log_file: str) -> logging.Logger:
    logger = logging.getLogger("gffACAKE")
    # Set level to Debug; capture everything

    logger.setLevel(logging.DEBUG)

    # prevent duplicate logs if rerun
    if logger.handlers:
        logger.handlers.clear()

    # logger output message
    format = logging.Formatter("%(levelname)s\t%(asctime)s\t%(message)s")
    filehandler = logging.FileHandler(log_file)
    filehandler.setLevel(logging.DEBUG)
    filehandler.setFormatter(format)
    logger.addHandler(filehandler)
    # Prevent log records from propagating to parent loggers
    logger.propagate = False
    return logger

