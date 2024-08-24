"""
Logging Configuration Module

This module provides a centralized logging configuration for the nigeria_geodata package.
It sets up a logger with a default warning level and a console handler to format and display log messages.

Authors:
    Emmanuel Jolaiya
    Samuel Adedoyin

Date:
    24/08/2024

The logger is configured to output messages to the console with the following format:
"nigeria_geodata:%(asctime)s - %(name)s - %(levelname)s - %(message)s"

Functions:
- configure_logging: Allows for customization of the logging level.

Usage:
    To use the logging configuration, import this module and call the `configure_logging`
    function to adjust the logging level as needed. The logger will automatically use the
    configured level and format for log messages.

    Example:
        from nigeria_geodata.utils import configure_logging

        # Set the logging level to DEBUG
        logger_module.configure_logging(logging.DEBUG)
"""

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

    Example:
        # Set logging level to INFO
        configure_logging(logging.INFO)
    """
    logger.setLevel(level)
    for handler in logger.handlers:
        handler.setLevel(level)
