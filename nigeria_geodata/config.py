"""
Module: config.py

Configuration settings module for managing API keys and data source settings.

Authors:
    Emmanuel Jolaiya
    Samuel Adedeyin
Date:
    24/08/2024

This module provides the `Config` class, which contains configuration settings
for various data sources, including URLs and other related information. It
includes methods to retrieve service URLs and detailed information about the
configured data sources.

Classes:
    Config: A class for managing and retrieving configuration settings related
    to data sources.

Usage:
    To use this module, access the `Config` class and call its static methods
    to retrieve configuration values and data source information.

Example:
    service_url = Config.get_service_url(DataSource.GRID3)
    service_info_url = Config.get_service_info_url(DataSource.GRID3)
    data_source_info = Config.get_data_source_info(DataSource.GRID3)
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
        DataSource.NGSA: {
            "NIGERIA_STATES_BOUNDARY_URL": "https://gist.githubusercontent.com/jeafreezy/0ae34d9f8a997d52bafdbc57437982f3/raw/f814ea50b4fd65e9eec1a0611082ef942ce11305/nigeria_states.geojson",
        },
    }

    @staticmethod
    def get_service_url(source: DataSourceInfo, url: str = "SERVICE_URL") -> str:
        """
        Get the service URL for a given data source.

        Args:
            source (DataSourceInfo): The data source for which to retrieve the URL.
            url (str): The key for the URL in the `DATA_SOURCES` dictionary. Defaults to "SERVICE_URL".

        Returns:
            str: The service URL for the specified data source, or None if not found.
        """

        return Config.DATA_SOURCES.get(source, {}).get(url)

    @staticmethod
    def get_service_info_url(source: DataSourceInfo) -> str:
        """
        Get the service info URL for a given data source.

        Args:
            source (DataSourceInfo): The data source for which to retrieve the info URL.

        Returns:
            str: The service info URL for the specified data source, or None if not found.
        """

        return Config.DATA_SOURCES.get(source, {}).get("SERVICE_INFO_URL")

    @staticmethod
    def get_data_source_info(source: DataSourceInfo) -> Dict[str, DataSourceInfo]:
        """
        Get the data source info URL for a given data source.

        Args:
            source (DataSourceInfo): The data source for which to retrieve the info URL.

        Returns:
            str: The datasource info URL for the specified data source, or None if not found.
        """
        sources = {ds.name: ds for ds in DataSource.list_sources()}
        return sources.get(source)
