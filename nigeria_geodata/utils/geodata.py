from nigeria_geodata.utils.common import GeodataUtils


class NigeriaAdmin(GeodataUtils):
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
