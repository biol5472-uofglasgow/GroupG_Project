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