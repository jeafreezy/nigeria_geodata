"""
AsyncBaseDataSource Module

This module defines the `AsyncBaseDataSource` class, which serves as an abstract
base class for asynchronous data retrieval from data sources.
It provides a blueprint for asynchronous interactions with data sources.

Authors:
    Emmanuel Jolaiya
    Samuel Adedoyin

Date:
    24/08/2024

Modules:
    AsyncBaseDataSource: An abstract base class that defines the essential asynchronous
    methods for interacting with geospatial data sources.

Overview:
    The `AsyncBaseDataSource` class outlines the required asynchronous methods that
    any concrete subclass must implement to support asynchronous operations. This
    design allows for consistent and uniform interaction with various geospatial
    data sources, providing an interface for listing, searching, and filtering data.

Key Features:
    - Asynchronous Methods: The class includes abstract asynchronous methods that
      subclasses must implement. These methods are `list_data()`, `search()`, and
      `filter()`.
    - Extensibility: Subclasses can extend this base class to integrate with specific
      data sources, ensuring compatibility with the defined asynchronous methods.
    - Reusability: By providing a common interface, this module facilitates the
      development of various data sources that adhere to a uniform approach for
      asynchronous data operations.

Classes:
    AsyncBaseDataSource: An abstract base class for asynchronous data sources. Defines
    methods that subclasses must implement to perform asynchronous operations.

Methods:
    list_data:
        An asynchronous method to list all available data from the data source.
    search:
        An asynchronous method to search for available data from the data source.
    filter:
        An asynchronous method to filter data from the data source.

Example:
    class MyAsyncDataSource(AsyncBaseDataSource):
        async def list_data(self, dataframe: bool = True):
            # Implementation here
            pass

        async def search(self, query: str, dataframe: bool = True):
            # Implementation here
            pass

        async def filter(self, data_name: str, state: Optional[str] = None,
                         bbox: Optional[List[float]] = None,
                         aoi_geometry: Geometry = None,
                         preview: bool = False):
            # Implementation here
            pass

        async def info(self, data_name: str, dataframe: bool = True):
            # Implementation here
            pass

    my_data_source = MyAsyncDataSource()
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


class AsyncBaseDataSource(metaclass=abc.ABCMeta):
    """
    Abstract base class for asynchronous data sources.

    This class provides an abstract interface for various geospatial data sources
    that support asynchronous operations. It defines essential asynchronous methods
    that any concrete subclass must implement.

    Methods:
        list_data():
            Asynchronously lists all available data from the data source.
        search():
            Asynchronously searches for available data from the data source.
        filter():
            Asynchronously filters data from the data source.

    Raises:
        NotImplementedError: If any of the abstract methods are not implemented by
        a subclass.
    """

    @abc.abstractmethod
    async def list_data(
        self, dataframe: bool = True
    ) -> Union[List[EsriFeatureServiceBasicInfo], Optional["pd.DataFrame"]]:
        """
        Asynchronously retrieves a list of all available data from the data source.

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
    async def search(
        self, query: str, dataframe: bool = True
    ) -> Union[List[EsriFeatureServiceBasicInfo], List, Optional["pd.DataFrame"]]:
        """
        Asynchronously searches for data based on the provided query.

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
    async def info(
        self, data_name: str, dataframe: bool = True
    ) -> Union[EsriFeatureLayerInfo, Optional["pd.DataFrame"], Dict[str, Any]]:
        """
        Asynchronously retrieves information about a specific data layer.

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
    async def filter(
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
        Asynchronously filters data based on parameters.

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
        Returns a string representation of the AsyncBaseDataSource instance.

        Returns:
            str: A string representation of the AsyncBaseDataSource instance.
        """
        return "<AsyncBaseDataSource>"
