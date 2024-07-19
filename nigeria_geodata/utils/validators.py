from typing import Union

from nigeria_geodata.models.common import Feature, FeatureCollection, Geometry


def validate_geojson(obj: Union[Feature, FeatureCollection]) -> None:
    """Validate if the object is a valid GeoJSON Feature or FeatureCollection."""
    if isinstance(obj, Feature):
        if obj.type != "Feature":
            raise ValueError("Invalid GeoJSON Feature type.")
        if not isinstance(obj.geometry, Geometry):
            raise ValueError("Invalid GeoJSON Feature geometry.")
    elif isinstance(obj, FeatureCollection):
        if obj.type != "FeatureCollection":
            raise ValueError("Invalid GeoJSON FeatureCollection type.")
        if not all(isinstance(f, Feature) for f in obj.features):
            raise ValueError("All items in FeatureCollection must be of type Feature.")

    raise ValueError("Object must be of type Feature or FeatureCollection.")
