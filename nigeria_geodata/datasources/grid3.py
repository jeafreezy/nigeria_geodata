"""

Grid3 data source implementation module.

Authors:

Date:

"""

from functools import cache
import json
from math import ceil
from typing import List, Optional, Union

from shapely.geometry import shape

from nigeria_geodata.async_core import AsyncBaseDataSource
from nigeria_geodata.config import Config
from nigeria_geodata.core import SyncBaseDataSource
from nigeria_geodata.datasources.base import DataSource
from nigeria_geodata.models.common import (
    EsriFeatureServiceBasicInfo,
    EsriFeatureServiceDetailedInfo,
    Feature,
    FeatureCollection,
)
from nigeria_geodata.utils.api import make_request
from nigeria_geodata.utils.common import GeodataUtils

from nigeria_geodata.utils.enums import NigeriaState
from nigeria_geodata.utils.validators import validate_geojson
import pandas as pd
from nigeria_geodata.utils import logger


class Grid3(SyncBaseDataSource):
    """
    A data source class for interacting with the GRID3 service.

    This class extends `SyncBaseDataSource` and is configured to interact 
    with the GRID3 data service, using predefined URLs for the service and 
    its associated information.

    Attributes:
        service_url (str): The URL to the GRID3 service layer.
        service_info_url (str): The URL to the GRID3 service information layer.
    """
    service_url: str = Config.get_service_url(DataSource.GRID3)
    service_info_url: str = Config.get_service_info_url(DataSource.GRID3)

    def __init__(self) -> None:
        super().__init__()
        # fetch and cache this at initialization for optimal performance
        self.feature_services = self._get_feature_services()

    @cache
    def _get_feature_services(self) -> List[EsriFeatureServiceBasicInfo]:
        """
        Retrieve a list of feature services available in the data source.

        This method queries the data source and returns a list of basic 
        information about the Esri feature services that are available.

        Returns:
            List[EsriFeatureServiceBasicInfo]: A list containing basic information 
            about each available Esri feature service.
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
        Check if the specified data name exists in the service layer and retrieve matching data.

        This method searches for feature services in the service layer that match the provided 
        data name and returns a list of `EsriFeatureServiceBasicInfo` objects corresponding 
        to the matches.

        Parameters:
            data_name (str): The name of the data to search for in the service layer.

        Returns:
            List[EsriFeatureServiceBasicInfo]: A list of `EsriFeatureServiceBasicInfo` objects 
            representing the data that matches the provided name.
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

    @cache
    def __get_max_features(self, service_url: str) -> int:
        """
        Retrieve the maximum number of features available in the specified service layer.

        This method queries the service layer at the given URL to determine the total number 
        of features available.

        Parameters:
            service_url (str): The URL of the service layer to query.

        Returns:
            int: The maximum number of features available in the specified service layer.
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

    @cache
    def list_data(
        self, dataframe: bool = True
    ) -> Union[List[EsriFeatureServiceBasicInfo], pd.DataFrame]:
        """
        List data available in the service layer.

        This method retrieves a list of Esri feature services available in the data source. 
        The data can be returned either as a list of `EsriFeatureServiceBasicInfo` objects 
        or as a pandas DataFrame, depending on the `dataframe` parameter.

        Parameters:
            dataframe (bool): If True, the data is returned as a pandas DataFrame. 
                            If False, the data is returned as a list of `EsriFeatureServiceBasicInfo` objects.
                            Default is True.

        Returns:
            Union[List[EsriFeatureServiceBasicInfo], pd.DataFrame]: 
                A list of `EsriFeatureServiceBasicInfo` objects or a pandas DataFrame 
                containing the available data, based on the `dataframe` parameter.
        """
        total_services = len(self.feature_services)
        logger.info(
            f"There is a total {total_services + 1} Nigeria geodata in the Grid3 database."
        )
        if dataframe:
            data = {
                "id": list(range(total_services)),
                "name": [
                    feature_service.name for feature_service in self.feature_services
                ],
            }
            return pd.DataFrame(data)
        return self.feature_services

    @cache
    def search(
        self, query: str, dataframe: bool = True
    ) -> Union[List[EsriFeatureServiceBasicInfo], pd.DataFrame]:
        """
        Search for feature services matching the query in the service layer.

        This method searches for Esri feature services that match the provided query string. 
        The search results can be returned either as a list of `EsriFeatureServiceBasicInfo` objects 
        or as a pandas DataFrame, depending on the `dataframe` parameter.

        Args:
            query (str): The search query string used to filter the feature services.
            dataframe (bool): If True, the search results are returned as a pandas DataFrame. 
                            If False, the results are returned as a list of `EsriFeatureServiceBasicInfo` objects.
                            Default is True.

        Returns:
            Union[List[EsriFeatureServiceBasicInfo], pd.DataFrame]: 
                A list of `EsriFeatureServiceBasicInfo` objects or a pandas DataFrame containing 
                the search results, based on the `dataframe` parameter.
        """

        search_results = list(
            filter(
                lambda feature_server: query.upper()
                in str(feature_server.name).upper(),
                self.feature_services,
            ),
        )

        total_results = len(search_results)
        logger.info(f"Search query for '{query}' returned {total_results + 1} results.")

        if dataframe:
            # they don't need to see the url when rendering the dataframe.
            data = {
                "id": list(range(total_results)),
                "name": [feature_service.name for feature_service in search_results],
            }
            return pd.DataFrame(data)

        return search_results

    @cache
    def info(
        self,
        data_name: str,
        dataframe: bool = True,
    ) -> Union[pd.DataFrame, EsriFeatureServiceDetailedInfo]:
        """
        Connect to a FeatureServer and retrieve more information about it.

        Parameters:
            id (int): The ID of the feature service.
            dataframe (bool): If True, returns the information as a pandas DataFrame.
                              If False, returns an EsriFeatureService object.

        Returns:
            Union[pd.DataFrame, EsriFeatureService]: A DataFrame or an EsriFeatureService object.
        """

        search_result = self.__find_and_validate_name(data_name)

        query_params = {"f": "json"}
        # incase it returns multiple just use the first one.
        feature_server = search_result[0]
        response = make_request(f"{feature_server.url}", query_params)
        feature_service = EsriFeatureServiceDetailedInfo(
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
        )
        if dataframe:
            data = feature_service.__dict__.copy()
            # to avoid confusing the users about the maximum data count
            data.pop("maxRecordCount", None)
            transformed_data = {"Key": list(data.keys()), "Value": list(data.values())}
            return pd.DataFrame(transformed_data)
        return feature_service

    def filter(
        self,
        data_name: str,
        state: Optional[str] = None,
        bbox: Optional[List[float]] = None,
        aoi_geojson: Optional[Union[Feature, FeatureCollection]] = None,
        geodataframe: bool = True,
        preview: bool = False,
    ) -> pd.DataFrame:   
        """
        Filter data from the service layer based on various criteria.

        This method filters Esri feature services using the specified criteria such as 
        data name, state, bounding box, or an area of interest (AOI) in GeoJSON format. 
        The filtered data is returned as a pandas DataFrame.

        Args:
            data_name (str): The name of the data to filter.
            state (Optional[str]): The specific state to filter the data by. Default is None.
            bbox (Optional[List[float]]): A bounding box to filter the data, specified as 
                                        [xmin, ymin, xmax, ymax]. Default is None.
            aoi_geojson (Optional[Union[Feature, FeatureCollection]]): A GeoJSON object representing 
                                                                    the area of interest to filter by. Default is None.
            geodataframe (bool): If True, returns the filtered data as a GeoDataFrame. 
                                If False, returns it as a regular pandas DataFrame. Default is True.
            preview (bool): If True, returns a preview of the filtered data, typically limited in size. 
                            Default is False.

        Returns:
            pd.DataFrame: The filtered data as a pandas DataFrame or GeoDataFrame, based on the `geodataframe` parameter.
        """

        # get the feature service information
        feature_service = self.info(data_name, False)

        # todo confirm that the service support query?

        # only one parameter can be provided, so this check is to ensure that.
        params = sum([state is not None, bbox is not None, aoi_geojson is not None])

        if params != 1:
            raise ValueError(
                "Exactly one parameter (state, bbox, or aoi_geojson) must be provided."
            )

        # State validation
        esri_geometry = None
        # default to the esriGeometryEnvelope which is like the bbox.
        geometryType = "esriGeometryEnvelope"

        if state is not None:
            if isinstance(state, str):
                assert state.lower() in [
                    x.value.lower() for x in NigeriaState
                ], "The provided state is not a valid Nigeria State."
            # update esri geometry
            esri_geometry = GeodataUtils.get_state_bbox(NigeriaState.ABIA.name)

        # BBox validation
        if bbox is not None:
            if isinstance(bbox, list):
                if len(bbox) != 4 or not all(
                    isinstance(coord, (int, float)) for coord in bbox
                ):
                    raise ValueError(
                        "The provided bbox is invalid. It should be a list of four numeric values."
                    )
            # update esribbox
            esri_geometry = bbox

        # GeoJSON validation
        if aoi_geojson is not None:
            if isinstance(aoi_geojson, (Feature, FeatureCollection)):
                validate_geojson(aoi_geojson)
            elif isinstance(aoi_geojson, str):
                try:
                    obj = json.loads(aoi_geojson)
                    if obj.get("type") == "Feature":
                        feature = Feature(**obj)
                        validate_geojson(feature)
                    elif obj.get("type") == "FeatureCollection":
                        feature_collection = FeatureCollection(**obj)
                        validate_geojson(feature_collection)
                    else:
                        raise ValueError("Invalid GeoJSON string.")
                except (json.JSONDecodeError, ValueError) as e:
                    raise ValueError(f"Invalid GeoJSON string: {e}")
            else:
                raise ValueError(
                    "The provided GeoJSON must be a Feature, FeatureCollection, or a JSON string representing one of these."
                )

            # compute the bbox for the geojson, no need to check the type again
            # even if the user pass in a point, we can always use a bbox filter, at least for now
            # geometryType = GeodataUtils.geojson_to_esri_type(aoi_geojson.geometry.type)
            esri_geometry = shape(aoi_geojson.geometry).bounds

        # build the query

        params = {
            "where": "FID > 0",  # this is required. We're assuming all data has `FID` here.
            "geometryType": geometryType,
            "f": "geojson",  # check the supported formats to know the one to use, if geojson is not supported, then use json and later convert to geojson
        }

        # update the params if the user filters by state or bbox
        # According to the docs, geometry bbox only works when the geometry type is "esriGeometryEnvelope"
        # This would have been a challenge, but we would convert all the inpute geometry to bbox to alleviate it.

        if esri_geometry:
            params.update({"geometry": ",".join(map(str, esri_geometry))})

        req_url = f"{feature_service.featureServerURL}/{feature_service.layers[0]['id']}/query"
        max_features = self.__get_max_features(req_url)
        if max_features == 0:
            return []
        result_list = []
        resultOffset = 0
        max_request = ceil(max_features / feature_service.maxRecordCount)
        for _ in range(max_request):
            params["resultOffset"] = resultOffset
            response = make_request(req_url, params=params)
            features = response["features"]
            result_list.extend(features)
            resultOffset += feature_service.maxRecordCount
        if geodataframe:
            # should we support geodataframe when the user has geopandas in their environment
            # or when they install it during installation ?
            return pd.DataFrame(result_list)
        return result_list

    def __repr__(self) -> str:
        return "<Grid3>"


class AsyncGrid3(AsyncBaseDataSource):
    service_url: str = Config.get_service_url(DataSource.GRID3)

    async def list_data(self):
        # list available datasets in the data source
        # preview = true to preview on a static map as thumbnail, interactive = true to preview on interactive map e.g lon board
        ...

    def __repr__(self) -> str:
        return "<AsyncGrid3Data>"


if __name__ == "__main__":
    grid3 = Grid3()

    # search for the specific dataset you need

    search_results = grid3.search(query="health", dataframe=False)
    # see all available datasets
    # specify to get result as dataframe or not

    # idea: make pandas an optional dependency ?
    # all_data = grid3.list_data(dataframe=False)

    # get more information about a particular dataset
    health_data_info = grid3.info(search_results[2].name)

    # filter for an area or interest, state name or bbox
    # this can also support preview if you pass preview to be true
    health_data_info = grid3.filter(search_results[2].name, "lagos")
    print(health_data_info)
    # preview the data
    # download the data - same logic as filter, they can provide different filtering mechanism or none, and the path to save the file.
