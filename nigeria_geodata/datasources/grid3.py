"""

Grid3 data source implementation module.

Authors:

Date:

"""

from functools import cache

import logging
from math import ceil
from typing import List, Optional, Union


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
from nigeria_geodata.utils import logger, configure_logging


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
    ) -> Union[List[EsriFeatureServiceBasicInfo]]:
        """List available datasets from the datasource"""
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
    ) -> Union[List[EsriFeatureServiceBasicInfo]]:
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
            f"Search query for '{query}' did not match any available datasets. Use `grid3.list_data()` to see available datasets."
        )
        return []

    def info(
        self, data_name: str, dataframe: bool = True
    ) -> Union[EsriFeatureLayerInfo]:
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
            # to avoid confusing the users about the maximum data count
            data.pop("maxRecordCount", None)
            transformed_data = {"Key": list(data.keys()), "Value": list(data.values())}
            return pd.DataFrame(transformed_data)
        return feature_service.__dict__

    def filter(
        self,
        data_name: str,
        state: Optional[str] = None,
        bbox: Optional[List[float]] = None,
        aoi_geojson: Geometry = None,  # requires shapely, but check and let the user know they need to install shapely?
        preview: bool = False,  # requires lonboard which also requires geopandas, so this must ensure there is lonboard and geopandas
    ):
        feature_service = self.info(data_name, False)

        # only one parameter can be provided, so this check is to ensure that.
        params = sum([state is not None, bbox is not None, aoi_geojson is not None])

        if params != 1:
            raise ValueError(
                "Exactly one parameter (state, bbox, or aoi_geojson) must be provided."
            )

        # defaults
        esri_geometry = None
        geometryType = "esriGeometryEnvelope"  # default to the esriGeometryEnvelope which is like the bbox.

        # State validation
        if state:
            assert (
                state.lower() in [x.value.lower() for x in NigeriaState]
            ), f"The provided state is not a valid Nigeria State. Available states are: {[x.name for x in NigeriaState]}"
            # update esri geometry
            esri_geometry = GeodataUtils.get_state_bbox(state)

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

        # GeoJSON validation
        if aoi_geojson:
            # update the geometry type
            geometryType = GeodataUtils.geojson_to_esri_type(aoi_geojson["type"])
            esri_geometry = GeodataUtils.geojson_to_esri_json(aoi_geojson)

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
            if aoi_geojson:
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

        if len(result_list) > 0:
            gpd = CheckDependencies.geopandas()
            gdf = gpd.GeoDataFrame.from_features(
                result_list, crs=f"EPSG:{feature_service['spatialReference']['wkid']}"
            )
            if preview:
                viz = CheckDependencies.lonboard()
                return viz(gdf)
            # otherwise return the gdf
            return gdf
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
    configure_logging(logging.DEBUG)
    grid3 = Grid3()

    # search for the specific dataset you need

    search_results = grid3.search(query="health", dataframe=False)
    print(search_results)
    # see all available datasets
    # specify to get result as dataframe or not

    # idea: make pandas an optional dependency ?
    # all_data = grid3.list_data()

    # # get more information about a particular dataset
    health_data_info = grid3.info(search_results[2]["name"])
    # print(health_data_info)
    # # filter for an area or interest, state name or bbox
    # # this can also support preview if you pass preview to be true

    abuja = {
        "type": "Polygon",
        "coordinates": [
            [
                [7.67238899070153, 9.411277743470464],
                [7.719591613614795, 9.346354492650503],
                [7.730054867765653, 9.33196349327467],
                [7.667605864807296, 9.303650865823396],
                [7.603319118750131, 9.161440866254003],
                [7.588679365597071, 9.129055992709448],
                [7.592266990284626, 8.924564364697154],
                [7.594658867462671, 8.856400492018963],
                [7.591669114033247, 8.834875115658646],
                [7.565301365788063, 8.785279241049718],
                [7.541442864752658, 8.74040311720757],
                [7.5019798649085, 8.66865161494098],
                [7.496000739627068, 8.654301615795815],
                [7.493228492469344, 8.65073686485621],
                [7.4792584938284, 8.632776239657048],
                [7.477623487864993, 8.631333365597213],
                [7.443030865078008, 8.5932817402168],
                [7.418127113138021, 8.56990236521378],
                [7.38915723993034, 8.5455074895479],
                [7.368616617069182, 8.529128989284942],
                [7.342399617991854, 8.510438864012112],
                [7.312413239385601, 8.50078199108101],
                [7.271183991946438, 8.492465989931919],
                [7.210765363160833, 8.48096086713188],
                [7.162990988851832, 8.473337117086784],
                [7.11674123785723, 8.46622186620111],
                [7.084213742435283, 8.46368024370573],
                [7.057121737894344, 8.462964990203917],
                [7.025258118230123, 8.461647990307892],
                [6.991440740707198, 8.459823618719618],
                [6.984174740196291, 8.459377243126793],
                [6.827889862436032, 8.457549993573364],
                [6.778522487526533, 8.457549993744959],
                [6.784782863822441, 8.991261491241401],
                [6.786707365437382, 9.155335367553638],
                [6.788054490183914, 9.270166369378135],
                [7.015266867342825, 9.26897049246719],
                [7.03007511517467, 9.257713365980083],
                [7.167658364603656, 9.153118117645125],
                [7.219757990204025, 9.11351011747923],
                [7.233965866095348, 9.133501992184573],
                [7.249756865348898, 9.155721616078473],
                [7.388168363904934, 9.349822990066782],
                [7.393835989854549, 9.353999119481715],
                [7.39853861692722, 9.357463869954966],
                [7.417672116930958, 9.36703111926685],
                [7.445176614027172, 9.369422867499107],
                [7.463114741913456, 9.36822699032303],
                [7.476269239856355, 9.370618866833878],
                [7.496598739331612, 9.362247494624235],
                [7.50975273839554, 9.361051618025659],
                [7.58987524310246, 9.431607244136378],
                [7.67238899070153, 9.411277743470464],
            ]
        ],
    }

    health_data_info = grid3.filter(search_results[2]["name"], aoi_geojson=abuja)

    print(health_data_info)
    # preview the data
    # download the data - same logic as filter, they can provide different filtering mechanism or none, and the path to save the file.
