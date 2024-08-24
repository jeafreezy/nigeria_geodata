"""
Geospatial Utilities for Nigeria Admin Boundaries

This module defines the `NigeriaAdmin` class, which extends the `GeodataUtils` class
from the `nigeria_geodata.utils.common` module. The `NigeriaAdmin` class includes
static methods to handle geospatial data specific to Nigeria's administrative regions.

The methods provided are intended for internal use and handle the conversion between
GeoJSON types and ESRI formats, as well as validation of GeoJSON geometries.

Classes:
    NigeriaAdmin: A class that provides utilities for handling geospatial data related
                  to Nigeria's administrative regions.

Usage:
    To use this class, create an instance of `NigeriaAdmin` and call the methods as needed.
    Note that the methods are primarily intended for internal use.

    Example:
        from nigeria_geodata.utils import NigeriaAdmin

        states = NigeriaAdmin.get_states()

"""

from nigeria_geodata.utils.common import GeodataUtils


class NigeriaAdmin(GeodataUtils):
    """
    Provides utilities for geospatial data related to Nigeria's administrative regions.
    """

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def geojson_to_esri_type(geojson_type: str) -> str:
        """
        Not intended for public use.
        """
        ...

    @staticmethod
    def geojson_to_esri_json():
        """
        Not intended for public use.
        """
        ...

    @staticmethod
    def validate_geojson_geometry():
        """
        Not intended for public use.
        """
        ...
