"""

Grid3 data source implementation module.

Authors:

Date:

"""

from functools import cache
import json
from math import ceil
from typing import List, Optional, Union

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
from nigeria_geodata.utils.common import (
    geojson_to_esri_type,
)

from nigeria_geodata.utils.enums import NigeriaState
from nigeria_geodata.utils.validators import validate_geojson
import pandas as pd
from nigeria_geodata.utils.logging import logger


class Grid3(SyncBaseDataSource):
    service_url: str = Config.get_service_url(DataSource.GRID3)
    service_info_url: str = Config.get_service_info_url(DataSource.GRID3)

    def __init__(self) -> None:
        super().__init__()
        # fetch and cache this at initialization for optimal performance
        self.feature_services = self._get_feature_services()

    @cache
    def _get_feature_services(self) -> List[EsriFeatureServiceBasicInfo]:
        """
        Retrieve the feature servers with Nigeria data from the ArcGIS Server root directory,
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
        """List available datasets from the datasource"""
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
        data_name: str,  # if the data name is provided, it means statename is to filter
        state: Optional[str] = None,
        bbox: Optional[List[float]] = None,  # bbox is to filter the provided data name
        aoi_geojson: Optional[
            Union[Feature, FeatureCollection]
        ] = None,  # to filter the provided data name
        geodataframe: bool = True,
        preview: bool = False,
    ) -> pd.DataFrame:
        """
        Filter the service across multiple layers.
        """

        # get the feature service information

        feature_service = self.info(data_name, False)

        # todo confirm that the service support query?
        # get the total data in the layers
        # get the maximum offset in the info so as to make the request in a loop

        # only one parameter can be provided, so this check is to ensure that.
        params = sum([state is not None, bbox is not None, aoi_geojson is not None])

        if params != 1:
            raise ValueError(
                "Exactly one parameter (state, bbox, or aoi_geojson) must be provided."
            )

        # State validation
        # esri_bbox = None
        # default to the esriGeometryEnvelope which is like the bbox.
        # only change it when the user provide an aoi
        geometryType = "esriGeometryEnvelope"

        if state is not None:
            if isinstance(state, str):
                assert state in [
                    x.value for x in NigeriaState
                ], "The provided state is not a valid Nigeria State."

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

            # update geometry type
            geometryType = geojson_to_esri_type(aoi_geojson.geometry.type)

        # build the query
        # get first layer id and the id

        params = {
            # get layer id from featureinfo ? because for now we're adding 1  to the query url
            "where": "FID > 0",  # this is required. We're assuming all data has `FID` here.
            "geometryType": geometryType,
            "f": "geojson",  # check the supported formats to know the one to user, if geojson is not supported, then use json and convert to geojson
        }
        req_url = f"{feature_service.featureServerURL}/{feature_service.layers[0]['id']}/query"
        max_features = self.__get_max_features(req_url)
        if max_features == 0:
            return []
        result_list = []
        resultOffset = 0
        max_request = ceil(max_features / feature_service.maxRecordCount)
        for _ in range(max_request):
            params["resultOffset"] = resultOffset
            features = make_request(req_url, params=params)["features"]
            result_list.extend(features)
            resultOffset += feature_service.maxRecordCount
        if geodataframe:
            # geodataframe ?
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

    ogun_results = grid3.search(query="ogun", dataframe=False)

    # see all available datasets
    # specify to get result as dataframe or not

    # idea: make pandas an optional dependency ?
    # all_data = grid3.list_data(dataframe=False)

    # get more information about a particular dataset
    health_data_info = grid3.info(ogun_results[0].name)

    # filter for an area or interest, state name or bbox
    # this can also support preview if you pass preview to be true
    health_data_info = grid3.filter(ogun_results[0].name, "Lagos")
    print(health_data_info)
    # preview the data
    # download the data - same logic as filter, they can provide different filtering mechanism or none, and the path to save the file.
