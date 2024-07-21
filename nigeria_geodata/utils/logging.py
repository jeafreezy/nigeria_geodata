import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
console_handler = logging.StreamHandler()
formatter = logging.Formatter(
    "nigeria_geodata:%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


def configure_logging(level=logging.WARNING):
    """
    Configure the logging level for the package.

    Args:
        level (int): Logging level (e.g., logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR)
    """
    logger.setLevel(level)
    for handler in logger.handlers:
        handler.setLevel(level)
