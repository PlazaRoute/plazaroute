import sys
import logging

logger = logging.getLogger('plaza_routing')


def setup_logging(verbose=False, quiet=False):
    logger.setLevel(logging.INFO)
    console_handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
            '[%(levelname)-7s] - %(message)s')
    if verbose and not quiet:
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - [%(levelname)-7s] - %(message)s')
    if quiet:
        logger.setLevel(logging.WARNING)

    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    logger.debug("Setting up logging complete")
