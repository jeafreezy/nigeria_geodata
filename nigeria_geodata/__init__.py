"""
nigeria_geodata Package

This package provides access to various data sources and utilities related to
geospatial data for Nigeria. It includes classes for interacting with the GRID3
data source and utilities for handling Nigerian administrative data.

Authors:
    Emmanuel Jolaiya
    Samuel Adedoyin

Date:
    24/08/2024

Modules:
- datasources: Contains data source classes for accessing and manipulating
  geospatial data.
  - grid3: Provides `Grid3` and `AsyncGrid3` classes for synchronous and
    asynchronous interactions with the GRID3 data source.
- utils: Includes utility functions and classes for geospatial data processing.
  - geodata: Provides the `NigeriaAdmin` class for administrative data related
    to Nigerian states.

Attributes:
- __version__: The version of the nigeria_geodata package.

Public API:
- Grid3: Class for synchronous interactions with the GRID3 data source.
- AsyncGrid3: Class for asynchronous interactions with the GRID3 data source.
- NigeriaAdmin: Utility class for Nigerian administrative data.

Usage:
    Import the classes and utilities as needed to interact with geospatial data.
    Example:
        from nigeria_geodata import Grid3, NigeriaAdmin
"""

from nigeria_geodata.datasources.grid3 import Grid3, AsyncGrid3
from nigeria_geodata.utils.geodata import NigeriaAdmin

__version__ = "0.0.9"

__all__ = ["Grid3", "AsyncGrid3", "NigeriaAdmin"]
