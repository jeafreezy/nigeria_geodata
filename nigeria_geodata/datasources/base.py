"""
Datasource management for nigeria_geodata.

This module defines and manages the metadata for supported data sources within the nigeria_geodata package.
Each data source is represented as a `DataSourceInfo` object that holds the name, URL, and description of the source.

Authors:
    Emmanuel Jolaiya
    Samuel Adedoyin

Date:
    24/08/2024

Classes:
    - DataSource: Contains predefined data sources and methods to retrieve them.

Attributes:
    - GRID3: Information on the GRID3 data source, which provides population estimates, settlements, subnational boundaries, and critical infrastructure for Nigeria.
    - NGSA: Information on the Nigeria Geological Survey Agency (NGSA) data source.

Methods:
    - list_sources: Returns a list of all available data sources.
"""

from typing import List
from nigeria_geodata.models.common import DataSourceInfo


class DataSource:
    """
    Class for managing the metadata of the supported data sources.
    """

    GRID3 = DataSourceInfo(
        name="GRID3",
        url="https://grid3.org/",
        description=(
            "GRID3 has country-wide data available for Nigeria, in collaboration with "
            "our partners CIESIN at Columbia University and WorldPop at the University of Southampton. "
            "Our data includes population estimates, settlements, subnational boundaries, and critical infrastructure."
        ),
    )
    NGSA = DataSourceInfo(
        name="NGSA",
        url="https://ngsa.gov.ng/",
        description=("Nigeria Geological Survey Agency"),
    )

    @classmethod
    def list_sources(cls) -> List[DataSourceInfo]:
        """
        Retrieve a list of all available data sources.

        This method returns a list of `DataSourceInfo` objects, each containing
        the name, URL, and description of the supported data sources for the
        nigeria_geodata package.

        Returns:
            List[DataSourceInfo]: A list of metadata about the available data sources.
        """
        return [cls.GRID3]
