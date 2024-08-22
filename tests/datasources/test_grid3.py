import pandas as pd
from unittest.mock import MagicMock, patch
import pytest
from nigeria_geodata import Grid3, AsyncGrid3
import geopandas as gpd

from nigeria_geodata.models.common import (
    EsriFeatureServiceBasicInfo,
)
from lonboard._map import Map

from nigeria_geodata.utils.enums import NigeriaState


# Sample mock data
mock_feature_services = [
    {"name": "Service1", "url": "http://example.com/1", "type": "FeatureServer"},
    {"name": "Service2", "url": "http://example.com/2", "type": "FeatureServer"},
]

SAMPLE_GEOMETRY = {
    "type": "Polygon",
    "coordinates": [
        [
            [3.2707, 6.4605],
            [3.2707, 6.6403],
            [3.6004, 6.6403],
            [3.6004, 6.4605],
            [3.2707, 6.4605],
        ]
    ],
}
mock_service_info = {
    "layerName": "fc_poi_church",
    "layerGeometryType": "esriGeometryPoint",
    "layerObjectIdField": "FID",
    "layerLastUpdated": "2022-10-19 22:11:26.564000",
    "layerId": 0,
    "totalFeatures": 33103,
    "serviceItemId": "3e9c65a6b8414f61a16c4426bb2e5e2a",
    "serviceDescription": "Churches in Nigeria",
    "maxRecordCount": 1000,
    "supportedQueryFormats": "JSON",
    "supportedExportFormats": "csv,shapefile,sqlite,geoPackage,filegdb,featureLayer",
    "capabilities": "Query",
    "description": "<div style='text-align:left;'><p><span style='...",
    "copyrightText": "eHealth Africa and Proxy Logics. 2020. Churches in Nigeria",
    "spatialReference": {"wkid": 4326, "latestWkid": 4326},
    "fullExtent": {
        "xmin": 2.720099999815204,
        "ymin": 4.293050000847259,
        "xmax": 14.72789999975603,
        "ymax": 13.725950000685817,
    },
    "layers": [{"id": 0, "name": "fc_poi_church", "parentLayerId": -1}],
    "tables": [],
    "featureServerURL": "http://example.com/1/FeatureServer",
}


# Mock DataFrame
mock_dataframe = pd.DataFrame(mock_feature_services)


def test_list_data():
    grid3 = Grid3()

    # Mock list_data method
    grid3.list_data = MagicMock(side_effect=[mock_feature_services, mock_dataframe])

    # Test the response when data is not in DataFrame
    feature_services = grid3.list_data(False)
    assert len(feature_services) > 0
    service = feature_services[0]
    assert "name" in service
    assert "url" in service
    assert "type" in service
    assert service["type"] == "FeatureServer"

    # Test the response when data is in DataFrame
    feature_services = grid3.list_data()
    assert isinstance(feature_services, pd.DataFrame)
    columns = list(feature_services.columns)
    assert "name" in columns
    assert "url" in columns


# Info tests


def test_data_info_success():
    grid3 = Grid3()

    # Mock list_data method to return valid service
    grid3.list_data = MagicMock(return_value=mock_feature_services)
    grid3.info = MagicMock(return_value=mock_service_info)

    service = grid3.list_data(False)[0]
    # Test without DataFrame response
    service_info = grid3.info(service["name"], False)
    expected_keys = list(mock_service_info.keys())
    assert list(service_info.keys()) == expected_keys

    # Test with DataFrame response
    grid3.list_data = MagicMock(return_value=mock_dataframe)
    grid3.info = MagicMock(return_value=mock_service_info)
    service = grid3.list_data()
    service_info = grid3.info(service["name"])
    assert list(service_info.keys()) == expected_keys


def test_data_info_failure():
    grid3 = Grid3()

    # Mock info method to raise ValueError for invalid data name
    grid3.info = MagicMock(
        side_effect=ValueError(
            "The provided data name 'wrong name' does not exist in the Grid3 database."
        )
    )

    with pytest.raises(ValueError) as exc_info:
        grid3.info("wrong name")

    assert (
        str(exc_info.value)
        == "The provided data name 'wrong name' does not exist in the Grid3 database."
    )


# Search tests


def test_search_success():
    grid3 = Grid3()

    # Mock search method to return mock data
    grid3.search = MagicMock(return_value=mock_dataframe)

    result = grid3.search("Health")
    assert isinstance(result, pd.DataFrame)
    columns = list(result.columns)
    assert "name" in columns
    assert "url" in columns

    # Test without DataFrame response
    grid3.search = MagicMock(return_value=mock_feature_services)
    result = grid3.search("Health", False)
    assert len(result) > 0
    selected = result[0]
    assert "name" in selected
    assert "url" in selected
    assert "type" in selected
    assert selected["type"] == "FeatureServer"


def test_search_failure():
    grid3 = Grid3()

    # Mock search method to return empty DataFrame
    grid3.search = MagicMock(return_value=pd.DataFrame())

    result = grid3.search("wrong name")
    assert len(result) == 0


# Filter method tests


def mock_response():
    return {
        "features": [
            {
                "geometry": {"type": "Point", "coordinates": [1, 2]},
                "properties": {"name": "Feature1"},
            },
            {
                "geometry": {"type": "Point", "coordinates": [3, 4]},
                "properties": {"name": "Feature2"},
            },
        ]
    }


def _mock_feature_services():
    return [
        EsriFeatureServiceBasicInfo(
            name="Service1",
            url="http://example.com/1",
            type="FeatureServer",
        )
    ]


@patch("nigeria_geodata.datasources.Grid3.info")
@patch("nigeria_geodata.datasources.grid3.make_request")
@patch("nigeria_geodata.datasources.Grid3._get_feature_services")
def test_filter_by_state(mock_get_feature_services, mock_make_request, mock_info):
    mock_get_feature_services.return_value = _mock_feature_services()
    mock_make_request.return_value = mock_response()
    mock_info.return_value = mock_service_info

    grid3 = Grid3()

    result = grid3.filter(data_name="Service1", state="Lagos")

    assert isinstance(result, gpd.GeoDataFrame)
    assert len(result) == 2
    assert result.crs == "EPSG:4326"

    # for preview mode
    preview_result = grid3.filter(data_name="Service1", state="Lagos", preview=True)
    assert isinstance(preview_result, Map)

    # Confirm the response data matches the mock
    assert result.shape[0] == len(mock_response()["features"])


@patch("nigeria_geodata.datasources.Grid3.info")
@patch("nigeria_geodata.datasources.grid3.make_request")
@patch("nigeria_geodata.datasources.Grid3._get_feature_services")
def test_filter_by_bbox(mock_get_feature_services, mock_make_request, mock_info):
    mock_get_feature_services.return_value = _mock_feature_services()
    mock_make_request.return_value = mock_response()
    mock_info.return_value = mock_service_info

    grid3 = Grid3()

    result = grid3.filter(data_name="Service1", bbox=[1.0, 2.0, 3.0, 4.0])

    assert isinstance(result, gpd.GeoDataFrame)
    assert len(result) == 2
    assert result.crs == "EPSG:4326"

    # for preview mode
    preview_result = grid3.filter(
        data_name="Service1", bbox=[1.0, 2.0, 3.0, 4.0], preview=True
    )
    assert isinstance(preview_result, Map)

    # Confirm the response data matches the mock
    assert result.shape[0] == len(mock_response()["features"])


@patch("nigeria_geodata.datasources.Grid3.info")
@patch("nigeria_geodata.datasources.grid3.make_request")
@patch("nigeria_geodata.datasources.Grid3._get_feature_services")
def test_filter_by_aoi_geometry(
    mock_get_feature_services, mock_make_request, mock_info
):
    mock_get_feature_services.return_value = _mock_feature_services()
    mock_make_request.return_value = mock_response()
    mock_info.return_value = mock_service_info

    grid3 = Grid3()

    result = grid3.filter(data_name="Service1", aoi_geometry=SAMPLE_GEOMETRY)

    assert isinstance(result, gpd.GeoDataFrame)
    assert len(result) == 2
    assert result.crs == "EPSG:4326"

    # for preview mode
    preview_result = grid3.filter(
        data_name="Service1",
        aoi_geometry=SAMPLE_GEOMETRY,
        preview=True,
    )
    assert isinstance(preview_result, Map)

    # Confirm the response data matches the mock
    assert result.shape[0] == len(mock_response()["features"])


@patch("nigeria_geodata.datasources.Grid3.info")
@patch("nigeria_geodata.datasources.grid3.make_request")
@patch("nigeria_geodata.datasources.Grid3._get_feature_services")
def test_filter_errors(mock_get_feature_services, mock_make_request, mock_info):
    mock_get_feature_services.return_value = _mock_feature_services()
    mock_make_request.return_value = mock_response()
    mock_info.return_value = mock_service_info

    grid3 = Grid3()

    # multiple parameters
    with pytest.raises(
        ValueError,
    ) as exc_info:
        grid3.filter(data_name="Service1", state="Lagos", bbox=[1.0, 2.0, 3.0, 4.0])
        assert (
            exc_info
            == "Only one parameter (state, bbox, or aoi_geometry) can be provided."
        )

    # invalid state name
    with pytest.raises(
        ValueError,
    ) as exc_info:
        grid3.filter(
            data_name="Service1",
            state="Lagos Invalid State",
        )
        assert (
            exc_info
            == f"The provided state 'Lagos Invalid State' is not a valid Nigeria State. Available states are: {', '.join([x.value.lower() for x in NigeriaState])}"
        )
    # invalid bbox
    with pytest.raises(
        ValueError,
    ) as exc_info:
        grid3.filter(data_name="Service1", bbox=[1.0, 2.0, 3.0, 4.0, 56.0])
        assert (
            exc_info
            == "The provided bbox is invalid. It should be a list of four numeric values."
        )
    # invalid geoemetry
    with pytest.raises(
        ValueError,
    ) as exc_info:
        SAMPLE_GEOMETRY = {
            "type": "Polygon",
            "coordinates": [
                [
                    [3.2707, 6.4605],
                    [3.2707, 6.4605],
                    [3.2707, 6.4605],
                    [23],
                ]
            ],
        }
        # validate invalid type
        grid3.filter(data_name="Service1", aoi_geometry=SAMPLE_GEOMETRY)
        assert exc_info == "The provided aoi_geometry is invalid"


################## ASYNC TESTS ####################


@pytest.mark.asyncio
@patch("nigeria_geodata.Grid3.list_data")
async def test_async_list_data(mock_list_data):
    mock_list_data.return_value = [
        EsriFeatureServiceBasicInfo(
            name="Service1", url="http://example.com", type="FeatureServer"
        )
    ]

    async_grid3 = AsyncGrid3()
    result = await async_grid3.list_data(dataframe=False)

    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0].name == "Service1"


@pytest.mark.asyncio
@patch("nigeria_geodata.Grid3.search")
async def test_async_search(mock_search):
    mock_search.return_value = [
        EsriFeatureServiceBasicInfo(
            name="Service1", url="http://example.com", type="FeatureServer"
        )
    ]

    async_grid3 = AsyncGrid3()
    result = await async_grid3.search(query="Health", dataframe=False)

    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0].name == "Service1"


@pytest.mark.asyncio
@patch("nigeria_geodata.Grid3.filter")
async def test_async_filter(mock_filter):
    mock_filter.return_value = [
        {
            "features": [
                {
                    "geometry": {"type": "Point", "coordinates": [1, 2]},
                    "properties": {"name": "Feature1"},
                }
            ]
        }
    ]

    async_grid3 = AsyncGrid3()
    result = await async_grid3.filter(
        data_name="Service1", state="Lagos", preview=False
    )

    assert isinstance(result, list)
    assert len(result) > 0


@pytest.mark.asyncio
@patch("nigeria_geodata.Grid3.info")
async def test_async_info(mock_info):
    mock_info.return_value = EsriFeatureServiceBasicInfo(
        name="Service1", url="http://example.com", type="FeatureServer"
    )

    async_grid3 = AsyncGrid3()
    result = await async_grid3.info(data_name="Service1", dataframe=False)

    assert isinstance(result, EsriFeatureServiceBasicInfo)
    assert result.name == "Service1"
