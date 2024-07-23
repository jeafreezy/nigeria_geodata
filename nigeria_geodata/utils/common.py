from functools import cache

from typing import Tuple

from nigeria_geodata.config import Config
from nigeria_geodata.datasources.base import DataSource
from nigeria_geodata.models.common import FeatureCollection
from nigeria_geodata.utils.api import make_request
from shapely.geometry import shape
from nigeria_geodata.utils import logger


class GeodataUtils:
    @staticmethod
    @cache
    def get_states() -> FeatureCollection:
        """
        Fetch the GeoJSON data from the github gist.

        Returns:
            Dict: The GeoJSON data as a dictionary.
        """
        service_url: str = Config.get_service_url(
            DataSource.NGSA, "NIGERIA_STATES_BOUNDARY_URL"
        )
        response = make_request(service_url)
        return response

    @staticmethod
    def get_state_bbox(state_name: str) -> Tuple[float, float, float, float]:
        """
        Get the bounding box for a given state.

        Args:
            state_name (str): The name of the state.

        Returns:
            Tuple[float, float, float, float]: The bounding box (minx, miny, maxx, maxy).
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
            return shape(state_geometry[0]["geometry"]).bounds
        else:
            msg = f"State '{state_name}' not found in the GeoJSON data."
            logger.error(msg)
            raise ValueError(msg)

    @staticmethod
    def geojson_to_esri_type(geojson_type: str) -> str:
        """
        Convert a GeoJSON geometry type to an ESRI geometry type.
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
