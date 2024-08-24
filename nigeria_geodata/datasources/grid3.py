"""
Grid3 data source implementation module.

This module provides synchronous and asynchronous classes for interacting
with the Grid3 dataset, which contains geospatial information on Nigeria.
It includes features like listing, searching, filtering, and retrieving
detailed information on datasets from the Grid3 database. The data is sourced
from ArcGIS servers.

Authors:
    Emmanuel Jolaiya
    Samuel Adedoyin

Date:
    24/08/2024
"""

import asyncio
from math import ceil
from typing import Any, Dict, List, Optional, Union, TYPE_CHECKING


if TYPE_CHECKING:
    import pandas as pd
    import geopandas as gpd
    from lonboard._map import Map


from nigeria_geodata.async_core import AsyncBaseDataSource
from nigeria_geodata.config import Config
from nigeria_geodata.core import SyncBaseDataSource
from nigeria_geodata.datasources.base import DataSource
from nigeria_geodata.models.common import (
    EsriFeatureLayerInfo,
    EsriFeatureServiceBasicInfo,
    Geometry,
)
from nigeria_geodata.utils.api import make_request
from nigeria_geodata.utils.common import (
    CheckDependencies,
    GeodataUtils,
    timestamp_to_datetime,
)

from nigeria_geodata.utils.enums import NigeriaState, RequestMethod
from nigeria_geodata.utils.logger import logger


class Grid3(SyncBaseDataSource):
    service_url: str = Config.get_service_url(DataSource.GRID3)
    service_info_url: str = Config.get_service_info_url(DataSource.GRID3)

    def __init__(self) -> None:
        super().__init__()
        # fetch at initialization for optimal performance
        self.feature_services = self._get_feature_services()

    def _get_feature_services(self) -> List[EsriFeatureServiceBasicInfo]:
        """
        Retrieve the available feature services containing Nigeria data from the ArcGIS Server root directory.

        This method fetches the feature services from the Grid3 server and filters out
        those relevant to Nigeria, identified by either "NGA" or "NIGERIA" in the service name.

        Returns:
            List[EsriFeatureServiceBasicInfo]: A list of feature services with basic metadata
                                               (name, URL, and type) relevant to Nigeria.
        """

        api_response = make_request(self.service_url)

        # based on review of the datasets, Nigeria is either represented as Nigeria or NGA
        # For now it works, but this has a potential for improvement.
        feature_services = list(
            map(
                lambda feature_service: EsriFeatureServiceBasicInfo(
                    feature_service["name"],
                    feature_service["url"],
                    feature_service["type"],
                ),
                filter(
                    lambda response_obj: "NGA" in str(response_obj["name"]).upper()
                    or "NIGERIA" in str(response_obj["name"]).upper(),
                    api_response.get("services", []),
                ),
            ),
        )
        self.feature_services = feature_services
        return feature_services

    def __find_and_validate_name(self, data_name) -> List[EsriFeatureServiceBasicInfo]:
        """
        Validate the existence of a dataset by name.

        This method checks if a dataset with the given name exists within the available
        Grid3 feature services. If it doesn't exist, it raises a ValueError.

        Args:
            data_name (str): The name of the dataset to search for.

        Returns:
            List[EsriFeatureServiceBasicInfo]: A list of matching feature services (if found).

        Raises:
            ValueError: If the provided data name does not exist in the Grid3 database.
        """
        data_exist = [
            service
            for service in self.feature_services
            if service.name.lower() == data_name.lower()
        ]
        if len(data_exist) == 0:
            msg = f"The provided data name '{data_name}' does not exist in the Grid3 database."
            logger.error(msg)
            raise ValueError(msg)
        return data_exist

    def __get_max_features(self, service_url: str) -> int:
        """
        Retrieve the maximum number of features available in a given feature service.

        This method makes a request to the Grid3 server to count the number of features
        in the dataset by performing a statistics query.

        Args:
            service_url (str): The URL of the feature service to query.

        Returns:
            int: The total number of features available in the dataset.
        """
        params = {
            "where": "FID > 0",
            "groupByFieldsForStatistics": "",
            "orderByFields": "",
            "returnDistinctValues": "true",
            "outStatistics": [
                [
                    {
                        "statisticType": "count",
                        "onStatisticField": "FID",
                        "outStatisticFieldName": "COUNT",
                    }
                ]
            ],
            "f": "json",
        }
        res = make_request(service_url, params=params)
        return res["features"][0]["attributes"]["COUNT"]

    def list_data(
        self, dataframe: bool = True
    ) -> Union[List[EsriFeatureServiceBasicInfo], Optional["pd.DataFrame"]]:
        """
        List available datasets from the Grid3 data source.

        This method retrieves a list of all datasets available in the Grid3 data source.
        It can return the information either as a list of `EsriFeatureServiceBasicInfo`
        objects or as a pandas DataFrame, depending on the `dataframe` parameter.

        Args:
            dataframe (bool): If True, returns the information as a pandas DataFrame.
                              If False, returns a list of `EsriFeatureServiceBasicInfo` objects.

        Returns:
            Union[List[EsriFeatureServiceBasicInfo], Optional["pd.DataFrame"]]: A list of
            `EsriFeatureServiceBasicInfo` objects or a pandas DataFrame containing dataset information.
        """
        total_services = len(self.feature_services)
        # Note: a feature server can have many layers, but inspecting the Grid3 service
        # all the feature server have a single layer for a single dataset
        # although the id of the layers are different.
        logger.info(
            f"There is a total {total_services + 1} Nigeria geodata in the Grid3 database."
        )
        if dataframe:
            pd = CheckDependencies.pandas()
            data = {
                "id": list(range(total_services)),
                "name": [
                    feature_service.name for feature_service in self.feature_services
                ],
            }
            return pd.DataFrame(data)
        # return a dict for those that don't want a dataframe or don't have pandas installed.
        return [x.__dict__ for x in self.feature_services]

    def search(
        self, query: str, dataframe: bool = True
    ) -> Union[List[EsriFeatureServiceBasicInfo], List, Optional["pd.DataFrame"]]:
        """
        Search the Grid3 data source for datasets matching a query string.

        This method searches for datasets whose names contain the specified query string.
        It can return the search results as a list of `EsriFeatureServiceBasicInfo`
        objects or as a pandas DataFrame, depending on the `dataframe` parameter.

        Args:
            query (str): The query string to search for in the dataset names.
            dataframe (bool): If True, returns the search results as a pandas DataFrame.
                              If False, returns a list of `EsriFeatureServiceBasicInfo` objects.

        Returns:
            Union[List[EsriFeatureServiceBasicInfo], List, Optional["pd.DataFrame"]]: A list of
            `EsriFeatureServiceBasicInfo` objects matching the query or a pandas DataFrame of results.
        """
        search_results = list(
            filter(
                lambda feature_server: query.upper()
                in str(feature_server.name).upper(),
                self.feature_services,
            ),
        )

        total_results = len(search_results)
        logger.info(f"Search query for '{query}' returned {total_results} results.")

        if len(search_results) > 0:
            if dataframe:
                pd = CheckDependencies.pandas()
                # they don't need to see the url when rendering the dataframe.
                data = {
                    "id": list(range(total_results)),
                    "name": [
                        feature_service.name for feature_service in search_results
                    ],
                }
                return pd.DataFrame(data)

            # return it as a list of dict
            return [x.__dict__ for x in search_results]
        print(
            f"Search query for '{query}' did not match any available datasets. Try another query or use `Grid3().list_data()` to see available datasets."
        )
        return []

    def info(
        self, data_name: str, dataframe: bool = True
    ) -> Union[EsriFeatureLayerInfo, Optional["pd.DataFrame"], Dict[str, Any]]:
        """
        Retrieve detailed information about a specific dataset from the Grid3 data source.

        This method provides detailed information about a dataset, including metadata and
        layer details, by connecting to the feature service. The information can be returned
        as an `EsriFeatureLayerInfo` object or as a pandas DataFrame, depending on the
        `dataframe` parameter.

        Args:
            data_name (str): The name of the dataset to retrieve information about.
            dataframe (bool): If True, returns the information as a pandas DataFrame.
                              If False, returns an `EsriFeatureLayerInfo` object.

        Returns:
            Union[EsriFeatureLayerInfo, Optional["pd.DataFrame"], Dict[str, Any]]: Detailed
            information about the dataset as an `EsriFeatureLayerInfo` object or a pandas DataFrame.
        """
        search_result = self.__find_and_validate_name(data_name)

        query_params = {"f": "json"}
        # incase it returns multiple just use the first one.
        feature_server = search_result[0]
        response = make_request(f"{feature_server.url}", query_params)
        # make a request to the actual layer to get the last edited date
        layer_response = make_request(
            f"{feature_server.url}/{response['layers'][0]['id']}", query_params
        )
        feature_service = EsriFeatureLayerInfo(
            layerName=layer_response["name"],
            layerGeometryType=layer_response["geometryType"],
            layerObjectIdField=layer_response["objectIdField"],
            layerId=response["layers"][0]["id"],
            serviceDescription=response["serviceDescription"],
            serviceItemId=response["serviceItemId"],
            maxRecordCount=response["maxRecordCount"],
            supportedQueryFormats=response["supportedQueryFormats"],
            supportedExportFormats=response["supportedExportFormats"],
            capabilities=response["capabilities"],
            description=response["description"],
            copyrightText=response["copyrightText"],
            spatialReference=response["spatialReference"],
            fullExtent=response["fullExtent"],
            layers=response["layers"],
            tables=response["tables"],
            featureServerURL=feature_server.url,
            layerLastUpdated=timestamp_to_datetime(
                layer_response["editingInfo"]["dataLastEditDate"]
            ),
            totalFeatures=self.__get_max_features(
                f"{feature_server.url}/{response['layers'][0]['id']}/query"
            ),
        )
        if dataframe:
            pd = CheckDependencies.pandas()
            data = feature_service.__dict__.copy()
            transformed_data = {"Key": list(data.keys()), "Value": list(data.values())}
            return pd.DataFrame(transformed_data)
        return feature_service.__dict__

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
        Filter datasets based on specified criteria and retrieve the results.

        This method filters the dataset based on the provided state, bounding box (bbox),
        or area of interest (aoi_geometry). It retrieves the filtered data and can return
        it as a GeoDataFrame, a preview map, or as a list of feature dictionaries.

        Args:
            data_name (str): The name of the dataset to filter.
            state (Optional[str]): The name of the Nigerian state to filter by (if applicable).
            bbox (Optional[List[float]]): The bounding box to filter by, defined as [xmin, ymin, xmax, ymax].
            aoi_geometry (Geometry): The area of interest geometry to filter by.
            preview (bool): If True, returns a preview map of the filtered results.
                            If False, returns the filtered data without a preview.
            geodataframe (bool): If True, returns the filtered data as a GeoDataFrame.
                                 If False, returns a list of feature dictionaries.

        Returns:
            Union[Optional["gpd.GeoDataFrame"], Optional["Map"], List[Dict[str, Any]]]:
            The filtered dataset as a GeoDataFrame, a preview map, or a list of feature dictionaries.
        """
        feature_service = self.info(data_name, False)

        # only one parameter can be provided, so this check is to ensure that.
        params = sum([state is not None, bbox is not None, aoi_geometry is not None])

        if params > 1:
            raise ValueError(
                "Only one parameter (state, bbox, or aoi_geometry) can be provided."
            )

        # defaults
        esri_geometry = None
        geometryType = "esriGeometryEnvelope"  # default to the esriGeometryEnvelope which is like the bbox.

        # State validation
        if state:
            valid_states = [x.value.lower() for x in NigeriaState]
            if state.lower() not in valid_states:
                raise ValueError(
                    f"The provided state '{state}' is not a valid Nigeria State. Available states are: {', '.join(valid_states)}"
                )
            # update esri geometry
            geometryType = "esriGeometryPolygon"
            esri_geometry = GeodataUtils.geojson_to_esri_json(
                GeodataUtils.get_state_geometry(state)
            )

        # bbox validation
        if bbox:
            if len(bbox) != 4 or not all(
                isinstance(coord, (int, float)) for coord in bbox
            ):
                raise ValueError(
                    "The provided bbox is invalid. It should be a list of four numeric values."
                )
            # update esribbox
            esri_geometry = bbox

        if aoi_geometry:
            if not GeodataUtils.validate_geojson_geometry(aoi_geometry):
                raise ValueError("The provided aoi_geometry is invalid.")

            geometryType = GeodataUtils.geojson_to_esri_type(aoi_geometry["type"])
            esri_geometry = GeodataUtils.geojson_to_esri_json(aoi_geometry)

        params = {
            "where": f"{feature_service['layerObjectIdField']} > 0",  # this is required
            "geometryType": geometryType,
            "f": "geojson",
            "outFields": "*",  # to return all the attributes of the data
            "spatialRel": "esriSpatialRelIntersects",
        }

        # update the params if the user filters by state or bbox
        if esri_geometry:
            if bbox:
                params.update({"geometry": ",".join(map(str, esri_geometry))})
            if aoi_geometry or state:
                params.update({"geometry": esri_geometry})

        max_features = feature_service["totalFeatures"]
        if max_features == 0:
            return []
        result_list = []
        resultOffset = 0
        max_request = ceil(max_features / feature_service["maxRecordCount"])
        for _ in range(max_request):
            params["resultOffset"] = resultOffset
            response = make_request(
                f"{feature_service['featureServerURL']}/{feature_service['layerId']}/query",
                params=params,
                method=RequestMethod.POST,
            )
            features = response["features"]
            result_list.extend(features)
            resultOffset += feature_service["maxRecordCount"]
            # check the length of the response, if it's less than the maxRecordCount then we can break
            # e.g when filtering, the result might not be up to 2000 i.e the maxRecordCount, so instead of making multiple requests
            # based on the total dataset i.e max_features, we can break it here.
            # an alternative is to hit the statistics endpoint with the filtering to get the maximum features for the query
            # but that's going to be another query. So this approach works fine for now.
            # Will require more testing.
            if len(features) < feature_service["maxRecordCount"]:
                break

        if geodataframe or preview:
            if len(result_list) > 0:
                gpd = CheckDependencies.geopandas()
                gdf = gpd.GeoDataFrame.from_features(
                    result_list,
                    crs=f"EPSG:{feature_service['spatialReference']['wkid']}",
                )
                if preview:
                    viz = CheckDependencies.lonboard()
                    return viz(gdf)
                # otherwise return the gdf
                return gdf
        return result_list

    def __repr__(self) -> str:
        return "<Grid3DataSource}>"


class AsyncGrid3(AsyncBaseDataSource):
    def __init__(self):
        self.sync_grid3 = Grid3()

    async def _run_sync(self, func, *args, **kwargs):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, func, *args, **kwargs)

    async def list_data(
        self, dataframe: bool = True
    ) -> Union[List[EsriFeatureServiceBasicInfo], Optional["pd.DataFrame"]]:
        return await self._run_sync(self.sync_grid3.list_data, dataframe)

    async def search(
        self, query: str, dataframe: bool = True
    ) -> Union[List[EsriFeatureServiceBasicInfo], List, Optional["pd.DataFrame"]]:
        return await self._run_sync(self.sync_grid3.search, query, dataframe)

    async def filter(
        self,
        data_name: str,
        state: Optional[str] = None,
        bbox: Optional[List[float]] = None,
        aoi_geometry: Geometry = None,
        preview: bool = False,
        geodataframe: bool = False,
    ) -> Union[
        Optional["gpd.GeoDataFrame"],
        Optional["Map"],
        List[Dict[str, Any]],
    ]:
        return await self._run_sync(
            self.sync_grid3.filter,
            data_name,
            state,
            bbox,
            aoi_geometry,
            preview,
            geodataframe,
        )

    async def info(
        self, data_name: str, dataframe: bool = True
    ) -> Union[EsriFeatureLayerInfo, Optional["pd.DataFrame"], Dict[str, Any]]:
        return await self._run_sync(self.sync_grid3.info, data_name, dataframe)

    def __repr__(self) -> str:
        return "<AsyncGrid3DataSource>"
