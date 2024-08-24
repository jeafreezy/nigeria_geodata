"""
Common Utilities Modules

This module provides utility functions and classes for handling geospatial data
related to Nigeria. It includes functionalities for fetching state boundaries,
converting GeoJSON to ESRI formats, validating GeoJSON geometries, and checking
for optional dependencies.

Authors:
    Emmanuel Jolaiya
    Samuel Adedoyin

Date:
    24/08/2024

Classes:
    GeodataUtils: Provides methods for fetching and processing Nigerian state
        boundary data, converting between GeoJSON and ESRI formats, and validating
        GeoJSON geometries.
    CheckDependencies: Provides methods to check and import optional dependencies
        like pandas, geopandas, typer, and lonboard.

Functions:
    timestamp_to_datetime: Converts a timestamp in milliseconds to a timezone-aware
        UTC datetime object.
"""

from functools import lru_cache
import datetime
from typing import TYPE_CHECKING, Any, Dict, Tuple

if TYPE_CHECKING:
    from shapely import Polygon

from nigeria_geodata.config import Config
from nigeria_geodata.datasources.base import DataSource
from nigeria_geodata.models.common import FeatureCollection
from nigeria_geodata.utils.api import make_request
from nigeria_geodata.utils import logger
from nigeria_geodata.utils.exceptions import PackageNotFoundError


class GeodataUtils:
    """
    A utility class for geodata operations including fetching state boundaries,
    converting GeoJSON types to ESRI types, and validating GeoJSON geometries.
    """

    @staticmethod
    @lru_cache(maxsize=None)
    def get_states() -> FeatureCollection:
        """
        Fetch the GeoJSON data for Nigerian states from a specified service URL.

        Returns:
            FeatureCollection: The GeoJSON data as a dictionary.
        """
        service_url: str = Config.get_service_url(
            DataSource.NGSA, "NIGERIA_STATES_BOUNDARY_URL"
        )
        response = make_request(service_url)
        return response

    @staticmethod
    def get_state_geometry(state_name: str) -> Tuple[float, float, float, float]:
        """
        Retrieve the bounding box for a given Nigerian state.

        Args:
            state_name (str): The name of the state to retrieve.

        Returns:
            Tuple[float, float, float, float]: The bounding box coordinates (minx, miny, maxx, maxy).

        Raises:
            ValueError: If the state is not found in the GeoJSON data.
        """

        states_geojson = GeodataUtils.get_states()

        state_geometry = list(
            filter(
                lambda feature: feature["properties"]["ADM1NAME_"].lower()
                == state_name.lower(),
                states_geojson["features"],
            )
        )
        if len(state_geometry) > 0:
            return state_geometry[0]["geometry"]
        else:
            msg = f"State '{state_name}' not found in the GeoJSON data."
            logger.error(msg)
            raise ValueError(msg)

    @staticmethod
    def geojson_to_esri_type(geojson_type: str) -> str:
        """
        Convert a GeoJSON geometry type to an ESRI geometry type.

        Args:
            geojson_type (str): The GeoJSON geometry type.

        Returns:
            str: The corresponding ESRI geometry type.

        Raises:
            ValueError: If the GeoJSON type is unsupported.
        """
        geojson_to_esri = {
            "Point": "esriGeometryPoint",
            "MultiPoint": "esriGeometryMultipoint",
            "LineString": "esriGeometryPolyline",
            "Polygon": "esriGeometryPolygon",
            "MultiPolygon": "esriGeometryPolygon",  # We can add this here since ESRI treats MultiPolygon similarly to Polygon
        }
        esri_type = geojson_to_esri.get(geojson_type)
        if not esri_type:
            raise ValueError(f"Unsupported GeoJSON type: {geojson_type}")
        return esri_type

    @staticmethod
    def geojson_to_esri_json(geojson_data: "Polygon"):
        """
        Convert GeoJSON geometry data to an ESRI JSON format.

        Args:
            geojson_data (Polygon): The GeoJSON geometry data.

        Returns:
            Dict[str, Any]: The ESRI JSON format of the geometry.

        Raises:
            ValueError: If the GeoJSON type is unsupported.
        """
        # Reference - https://developers.arcgis.com/rest/services-reference/enterprise/geometry-objects/
        if geojson_data["type"] == "Point":
            esri_json = {
                "x": geojson_data["coordinates"][0],
                "y": geojson_data["coordinates"][1],
            }

        elif geojson_data["type"] == "LineString":
            esri_json = {"paths": [geojson_data["coordinates"]]}

        elif geojson_data["type"] == "Polygon":
            esri_json = {"rings": geojson_data["coordinates"]}
        elif geojson_data["type"] == "MultiPolygon":
            esri_json = {
                "rings": [
                    ring for polygon in geojson_data["coordinates"] for ring in polygon
                ]
            }
        else:
            raise ValueError(
                f"Unsupported GeoJSON geometry type: {geojson_data['type']}"
            )

        return esri_json

    @staticmethod
    def validate_geojson_geometry(geometry: Dict[str, Any]) -> bool:
        """
        Validate the structure and coordinates of a GeoJSON geometry.

        Args:
            geometry (Dict[str, Any]): The GeoJSON geometry to validate.

        Returns:
            bool: True if the geometry is valid, False otherwise.
        """

        geom_type = geometry.get("type")
        coords = geometry.get("coordinates")

        if "type" not in geometry or "coordinates" not in geometry:
            return False

        # Validation based on the geometry type
        if geom_type == "Point":
            if not (
                isinstance(coords, list)
                and len(coords) == 2
                and all(isinstance(coord, (int, float)) for coord in coords)
            ):
                return False

        elif geom_type == "Polygon":
            if (
                not isinstance(coords, list)
                or len(coords) == 0
                or not all(isinstance(ring, list) for ring in coords)
                or not all(
                    isinstance(coord, list)
                    and len(coord) == 2
                    and all(isinstance(c, (int, float)) for c in coord)
                    for ring in coords
                    for coord in ring
                )
            ):
                return False

        elif geom_type == "LineString":
            if (
                not isinstance(coords, list)
                or len(coords) == 0
                or not all(
                    isinstance(coord, list)
                    and len(coord) == 2
                    and all(isinstance(c, (int, float)) for c in coord)
                    for coord in coords
                )
            ):
                return False

        elif geom_type == "MultiPoint":
            if (
                not isinstance(coords, list)
                or len(coords) == 0
                or not all(
                    isinstance(coord, list)
                    and len(coord) == 2
                    and all(isinstance(c, (int, float)) for c in coord)
                    for coord in coords
                )
            ):
                return False

        elif geom_type == "MultiLineString":
            if (
                not isinstance(coords, list)
                or len(coords) == 0
                or not all(
                    isinstance(line, list)
                    and len(line) > 0
                    and all(
                        isinstance(coord, list)
                        and len(coord) == 2
                        and all(isinstance(c, (int, float)) for c in coord)
                        for coord in line
                    )
                    for line in coords
                )
            ):
                return False

        elif geom_type == "MultiPolygon":
            if (
                not isinstance(coords, list)
                or len(coords) == 0
                or not all(
                    isinstance(polygon, list)
                    and len(polygon) > 0
                    and all(
                        isinstance(ring, list)
                        and len(ring) > 0
                        and all(
                            isinstance(coord, list)
                            and len(coord) == 2
                            and all(isinstance(c, (int, float)) for c in coord)
                            for coord in ring
                        )
                        for ring in polygon
                    )
                    for polygon in coords
                )
            ):
                return False

        else:
            return False

        return True


class CheckDependencies:
    """
    A utility class for checking and importing optional dependencies.
    """

    @staticmethod
    def pandas():
        """
        Check if the 'pandas' module is installed and return it if available.

        Returns:
            module: The imported 'pandas' module.

        Raises:
            PackageNotFoundError: If 'pandas' is not installed.
        """
        try:
            import pandas

            return pandas
        except PackageNotFoundError as err:
            # Raise an error with a message to install the missing package
            raise PackageNotFoundError(
                "pandas is required for rendering results as a dataframe.\n"
                "Run `pip install pandas`."
            ) from err

    @staticmethod
    def geopandas():
        """
        Check if the 'geopandas' module is installed and return it if available.

        Returns:
            module: The imported 'geopandas' module.

        Raises:
            PackageNotFoundError: If 'geopandas' is not installed.
        """
        try:
            import geopandas

            return geopandas
        except PackageNotFoundError as err:
            # Raise an error with a message to install the missing package
            raise PackageNotFoundError(
                "geopandas is required for rendering results as a geodataframe.\n"
                "Run `pip install geopandas`."
            ) from err

    @staticmethod
    def typer():
        """
        Check if the 'typer' module is installed and return it if available.

        Returns:
            module: The imported 'typer' module.

        Raises:
            PackageNotFoundError: If 'typer' is not installed.
        """
        try:
            import typer

            return typer
        except PackageNotFoundError as err:
            # Raise an error with a message to install the missing package
            raise PackageNotFoundError(
                "typer is required for CLI support.\n" "Run `pip install typer`."
            ) from err

    @staticmethod
    def lonboard():
        """
        Check if the 'lonboard' module is installed and return it if available.

        Returns:
            module: The imported 'lonboard' module.

        Raises:
            PackageNotFoundError: If 'lonboard' is not installed.
        """
        try:
            from lonboard import viz

            return viz
        except PackageNotFoundError as err:
            # Raise an error with a message to install the missing package
            raise PackageNotFoundError(
                "lonboard is required for map visualization.\n"
                "Run `pip install lonboard`."
            ) from err


def timestamp_to_datetime(timestamp_ms: int) -> datetime.datetime:
    """
    Converts a timestamp in milliseconds to a timezone-aware UTC datetime object.

    Args:
        timestamp_ms (int): The timestamp in milliseconds since the Unix epoch (January 1, 1970).

    Returns:
        datetime.datetime: A timezone-aware datetime object representing the input timestamp in UTC.

    Example:
        >>> timestamp_to_datetime(1633024800000)
        datetime.datetime(2021, 10, 1, 0, 0, tzinfo=datetime.timezone.utc)

    Notes:
        - The input timestamp is expected to be in milliseconds, so it is divided by 1000
          to convert it to seconds for compatibility with `datetime.utcfromtimestamp`.
        - The resulting datetime is set to UTC timezone using `datetime.timezone.utc`.
    """
    # Convert to seconds by dividing by 1000
    timestamp_sec = timestamp_ms / 1000

    # Convert to UTC datetime
    date_time = datetime.datetime.utcfromtimestamp(timestamp_sec)

    # Add UTC timezone info to the datetime object
    date_time = date_time.replace(tzinfo=datetime.timezone.utc)

    return date_time
