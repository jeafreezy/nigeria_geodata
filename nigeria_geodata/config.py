"""
Configuration settings module.
Authors:
Date:
"""

from typing import Dict
from nigeria_geodata.datasources.base import DataSource
from nigeria_geodata.models.common import DataSourceInfo


class Config:
    """
    Configuration class for managing API keys and data source settings.
    """

    DATA_SOURCES = {
        DataSource.GRID3: {
            "SERVICE_URL": "https://services3.arcgis.com/BU6Aadhn6tbBEdyk/ArcGIS/rest/services?f=json",
            "SERVICE_INFO_URL": "https://services3.arcgis.com/BU6Aadhn6tbBEdyk/ArcGIS/rest/info/?f=json",
        },
    }

    @staticmethod
    def get_service_url(source: DataSourceInfo) -> str:
        """
        Get the service URL for a given data source.

        Args:
            source (str): The name of the data source (e.g., 'GRID3').

        Returns:
            str: The service URL for the specified data source.
        """

        return Config.DATA_SOURCES.get(source, {}).get("SERVICE_URL")

    @staticmethod
    def get_service_info_url(source: DataSourceInfo) -> str:
        """
        Get the service URL for a given data source.

        Args:
            source (str): The name of the data source (e.g., 'GRID3').

        Returns:
            str: The service URL for the specified data source.
        """

        return Config.DATA_SOURCES.get(source, {}).get("SERVICE_INFO_URL")

    @staticmethod
    def get_health_check_url(source: DataSourceInfo) -> str:
        """
        Get the service URL for a given data source.

        Args:
            source (str): The name of the data source (e.g., 'GRID3').

        Returns:
            str: The service URL for the specified data source.
        """

        return Config.DATA_SOURCES.get(source, {}).get("HEALTH_CHECK_URL")

    @staticmethod
    def get_data_source_info(source: DataSourceInfo) -> Dict[str, DataSourceInfo]:
        """
        Get detailed information about a given data source.

        Args:
            source (str): The name of the data source (e.g., 'GRID3').

        Returns:
            DataSourceInfo: The detailed information for the specified data source.
        """
        sources = {ds.name: ds for ds in DataSource.list_sources()}
        return sources.get(source)

    #
