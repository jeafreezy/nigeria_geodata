"""
nigeria_geodata utilities module.

This module initializes the nigeria_geodata package by exposing core components like
logging configuration, administrative data for Nigeria, and state enumeration.

Authors:
    Emmanuel Jolaiya
    Samuel Adedoyin

Date:
    24/08/2024

Available imports:
    - configure_logging: Function to set up logging levels for the package.
    - logger: Logger instance for logging messages throughout the package.
    - NigeriaAdmin: Class for interacting with Nigerian administrative boundaries and geodata.
    - NigeriaState: Enum representing all Nigerian states and the Federal Capital Territory (FCT).

Usage:
    These components are imported into the package's namespace and can be accessed
    directly when the package is imported.

Example:
    from nigeria_geodata.utils import NigeriaAdmin, NigeriaState
"""

from .logger import configure_logging, logger
from .geodata import NigeriaAdmin
from .enums import NigeriaState

__all__ = ["configure_logging", "logger", "NigeriaAdmin", "NigeriaState"]
