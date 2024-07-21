def geojson_to_esri_type(geojson_type: str) -> str:
    """
    Convert a GeoJSON geometry type to an ESRI geometry type.
    """
    geojson_to_esri = {
        "Point": "esriGeometryPoint",
        "MultiPoint": "esriGeometryMultipoint",
        "LineString": "esriGeometryPolyline",
        "Polygon": "esriGeometryPolygon",
        "MultiPolygon": "esriGeometryPolygon",  # ESRI treats MultiPolygon similarly to Polygon
    }
    esri_type = geojson_to_esri.get(geojson_type)
    if not esri_type:
        raise ValueError(f"Unsupported GeoJSON type: {geojson_type}")
    return esri_type
