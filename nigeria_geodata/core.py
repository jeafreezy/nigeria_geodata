"""
Module: core.py

This module defines the abstract base class `SyncBaseDataSource`, which provides
an interface for synchronous data source operations. The class serves as a blueprint
for concrete implementations that interact with data sources in a synchronous manner.

The `SyncBaseDataSource` class outlines essential methods that any subclass must
implement to ensure consistent functionality across different data sources.

Authors:
    Emmanuel Jolaiya
    Samuel Adedoyin

Date:
    24/08/2024

Key Features:
- Abstract Methods: The class includes abstract methods that must be implemented
  by any concrete subclass. These methods are `list_data()`, `search()`, `filter()`,
  and `info()`.
- Reusability: By defining a common interface, this module facilitates the creation
  of various data sources with a uniform approach to synchronous data operations.
- Extensibility: Subclasses can extend this base class to integrate with specific
  data sources, ensuring compatibility with the defined methods.

Classes:
    SyncBaseDataSource: An abstract base class for synchronous data sources, defining
    the required methods that concrete implementations must provide.

Usage:
    To use this module, create a subclass of `SyncBaseDataSource` and implement
    the abstract methods to interact with your specific data source.

Example:
    class MyDataSource(SyncBaseDataSource):
        def list_data(self):
            # Implementation code
            pass

        def search(self):
            # Implementation code
            pass

        def filter(self):
            # Implementation code
            pass

        def info(self):
            # Implementation code
            pass
"""

import abc
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

from nigeria_geodata.models.common import (
    EsriFeatureLayerInfo,
    EsriFeatureServiceBasicInfo,
    Geometry,
)


if TYPE_CHECKING:
    import pandas as pd
    import geopandas as gpd
    from lonboard._map import Map


class SyncBaseDataSource(metaclass=abc.ABCMeta):
    """
    Abstract base class for data sources.

    This class provides an abstract interface for various geospatial data sources. It defines essential methods
    that any concrete subclass must implement.

    Methods:
        list_data():
            Lists all available data from the data source.
        search():
            Searches for available data from the data source.
        filter():
            Filters data from the data source.

    Raises:
        NotImplementedError: If any of the abstract methods are not implemented by
        a subclass.
    """

    @abc.abstractmethod
    def list_data(
        self, dataframe: bool = True
    ) -> Union[List[EsriFeatureServiceBasicInfo], Optional["pd.DataFrame"]]:
        """
        Retrieves a list of all available data from the data source.

        This method performs an operation to gather and return all the data available
        from the data source. The format of the returned data is determined by the
        `dataframe` flag.

        Args:
            dataframe (bool, optional): If True, returns the data as a pandas DataFrame.
                                        If False, returns the data as a list of
                                        `EsriFeatureServiceBasicInfo` objects or similar.
                                        Defaults to True.

        Returns:
            Union[List[EsriFeatureServiceBasicInfo], Optional["pd.DataFrame"]]:
                - If `dataframe` is True, returns a pandas DataFrame containing all available
                  data.
                - If `dataframe` is False, returns a list of `EsriFeatureServiceBasicInfo`
                  objects or a similar list representation.
                - May return None if no data is available, depending on the implementation.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def search(
        self, query: str, dataframe: bool = True
    ) -> Union[List[EsriFeatureServiceBasicInfo], List, Optional["pd.DataFrame"]]:
        """
        Searches for data based on the provided query.

        This method performs a search operation to retrieve data from the data source
        that matches the given search criteria. The format of the results depends
        on the `dataframe` flag.

        Args:
            query (str): The search query or criteria used to find relevant data from
                         the data source.
            dataframe (bool, optional): If True, returns the search results as a pandas
                                        DataFrame. If False, returns the results in a
                                        list format. Defaults to True.

        Returns:
            Union[List[EsriFeatureServiceBasicInfo], List, Optional["pd.DataFrame"]]:
                - If `dataframe` is True, returns a pandas DataFrame containing the search
                  results.
                - If `dataframe` is False, returns a list of results or a list of
                  `EsriFeatureServiceBasicInfo` objects.
                - If no results are found, may return an empty list or None depending on
                  the implementation.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def info(
        self, data_name: str, dataframe: bool = True
    ) -> Union[EsriFeatureLayerInfo, Optional["pd.DataFrame"], Dict[str, Any]]:
        """
        Retrieves information about a specific data layer.

        This method provides detailed information about the data layer specified by
        `data_name`. Depending on the `dataframe` flag, the method can return
        either a structured data object or a pandas DataFrame.

        Args:
            data_name (str): The name of the data layer for which information is requested.
            dataframe (bool, optional): If True, returns the information as a pandas DataFrame.
                                        If False, returns the information in its default format.
                                        Defaults to True.

        Returns:
            Union[EsriFeatureLayerInfo, Optional["pd.DataFrame"], Dict[str, Any]]:
                - If `dataframe` is True, returns a pandas DataFrame containing information
                about the specified data layer.
                - If `dataframe` is False, returns an `EsriFeatureLayerInfo` object or a
                dictionary containing the information about the data layer.
                - If the data layer information cannot be retrieved, may return None.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def filter(
        self,
        data_name: str,
        state: Optional[str] = None,
        bbox: Optional[List[float]] = None,
        aoi_geometry: Geometry = None,
        preview: bool = False,
        geodataframe: bool = True,
    ) -> Union[
        Optional["gpd.GeoDataFrame"],
        Optional["Map"],
        List[Dict[str, Any]],
    ]:
        """
        Filters data based on parameters.

        Args:
            data_name (str): Name of the data source.
            state (Optional[str]): Name of the state to filter by.
            bbox (Optional[List[float]]): Bounding box coordinates.
            aoi_geometry (Optional[Geometry]): Area of interest geometry.
            preview (bool): Whether to return a preview.

        Returns:
            Union[GeoDataFrame, Map, List[dict], None]: Filtered data or a map preview.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.
        """
        raise NotImplementedError

    def __repr__(self) -> str:
        """
        Returns a string representation of the SyncBaseDataSource instance.

        Returns:
            str: A string representation of the SyncBaseDataSource instance.
        """
        return "<SyncBaseDataSource>"
