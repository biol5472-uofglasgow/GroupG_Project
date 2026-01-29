import logging
from annot_consistency.logging_utils import logger

#### Unit testing for logger and models ####

# logger test
def test_logger(test_path):
    # create temporary log file path
    log_file = test_path / "test.log"

    # create logger and output message
    log = logger(str(log_file))
    log.info("the numbers mason, what do they mean")

    # Test suite 1; logger identity and level
    assert isinstance(log, logging.Logger)
    assert log.name == "gffACAKE"
    assert log.level == logging.DEBUG
    assert log.propagate is False

    # Suite 2: handler configs
    assert len(log.handlers) == 1
    handler = log.handlers[0]
    assert isinstance(handler, logging.FileHandler)
    assert handler.level == logging.INFO

    # Suite 3: Assert 3; formatter configuration
    format = handler.formatter
    assert format is not None
    assert "%(levelname)s" in format
    assert "%(asctime)s" in format
    assert "%(message)s" in format
