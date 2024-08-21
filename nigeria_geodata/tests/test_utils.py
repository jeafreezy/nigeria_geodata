import logging
import pytest
from unittest.mock import patch, MagicMock
import httpx
import json


from nigeria_geodata.utils import logger
from nigeria_geodata.utils.api import make_request, get_headers
from nigeria_geodata.utils.common import (
    CheckDependencies,
    GeodataUtils,
    timestamp_to_datetime,
)
from nigeria_geodata.utils.enums import RequestMethod
from nigeria_geodata.utils.exceptions import (
    HTTPStatusError,
    JSONDecodeError,
    PackageNotFoundError,
    RequestError,
)
from nigeria_geodata.utils.logger import configure_logging


def mock_get_headers():
    return get_headers()


SERVICE_URL = "https://example.com/api"
PARAMS = {"key": "value"}


# test API calls
@patch("nigeria_geodata.utils.api.get_headers", return_value=mock_get_headers())
@patch("httpx.Client.get")
def test_make_get_request_success(mock_get, mock_get_headers):
    mock_response = MagicMock()
    mock_response.json.return_value = {"success": True}
    mock_response.status_code = 200
    mock_get.return_value = mock_response

    result = make_request(SERVICE_URL, params=PARAMS, method=RequestMethod.GET)
    assert result == {"success": True}
    mock_get.assert_called_once_with(
        SERVICE_URL, headers=mock_get_headers(), params=PARAMS
    )


@patch("nigeria_geodata.utils.api.get_headers", return_value=mock_get_headers())
@patch("httpx.Client.post")
def test_make_post_request_success(mock_post, mock_get_headers):
    mock_response = MagicMock()
    mock_response.json.return_value = {"success": True}
    mock_response.status_code = 200
    mock_post.return_value = mock_response
    result = make_request(SERVICE_URL, params=PARAMS, method=RequestMethod.POST)
    assert result == {"success": True}
    mock_post.assert_called_once_with(
        SERVICE_URL, headers=mock_get_headers(), data=PARAMS
    )


@patch("nigeria_geodata.utils.api.get_headers", return_value=mock_get_headers())
@patch("httpx.Client.get")
def test_make_request_request_error(mock_get, mock_get_headers):
    mock_get.side_effect = httpx.RequestError("Request failed", request=MagicMock())
    with pytest.raises(RequestError):
        make_request(SERVICE_URL, params={}, method=RequestMethod.GET)


@patch("nigeria_geodata.utils.api.get_headers", return_value=mock_get_headers())
@patch("httpx.Client.get")
def test_make_request_http_status_error(mock_get, mock_get_headers):
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "404 Error", request=MagicMock(), response=mock_response
    )
    mock_get.return_value = mock_response
    with pytest.raises(HTTPStatusError):
        make_request(SERVICE_URL, params={}, method=RequestMethod.GET)


@patch("nigeria_geodata.utils.api.get_headers", return_value=mock_get_headers())
@patch("httpx.Client.get")
def test_make_request_json_decode_error(mock_get, mock_get_headers):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
    mock_get.return_value = mock_response

    with pytest.raises(JSONDecodeError):
        make_request(SERVICE_URL, params={}, method=RequestMethod.GET)


# test GeodataUtils

SAMPLE_GEOJSON = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {"ADM1NAME_": "Lagos"},
            "geometry": {
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
            },
        }
    ],
}


@pytest.fixture
def mock_make_request():
    with patch("nigeria_geodata.utils.common.GeodataUtils.get_states") as mock_request:
        mock_request.return_value = SAMPLE_GEOJSON
        yield mock_request


def test_get_states(mock_make_request):
    # Test if get_states correctly fetches the data
    result = GeodataUtils.get_states()
    assert result == SAMPLE_GEOJSON
    mock_make_request.assert_called_once()


def test_get_state_geometry_success(mock_make_request):
    # Test if get_state_geometry correctly returns geometry for a known state
    result = GeodataUtils.get_state_geometry("Lagos")
    expected_geometry = SAMPLE_GEOJSON["features"][0]["geometry"]
    assert result == expected_geometry


def test_get_state_geometry_state_not_found(mock_make_request):
    # Test if get_state_geometry raises an error for a non-existent state
    with pytest.raises(
        ValueError, match="State 'Wrong State' not found in the GeoJSON data."
    ):
        GeodataUtils.get_state_geometry("Wrong State")


def test_geojson_to_esri_type_valid():
    # Test if geojson_to_esri_type correctly converts GeoJSON types to ESRI types
    assert GeodataUtils.geojson_to_esri_type("Point") == "esriGeometryPoint"
    assert GeodataUtils.geojson_to_esri_type("Polygon") == "esriGeometryPolygon"


def test_geojson_to_esri_type_invalid():
    # Test if geojson_to_esri_type raises an error for unsupported types
    with pytest.raises(ValueError, match="Unsupported GeoJSON type: InvalidType"):
        GeodataUtils.geojson_to_esri_type("InvalidType")


def test_geojson_to_esri_json_polygon():
    # Test if geojson_to_esri_json correctly converts a GeoJSON Polygon to ESRI JSON
    polygon_geojson = {
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
    expected_esri_json = {"rings": polygon_geojson["coordinates"]}
    result = GeodataUtils.geojson_to_esri_json(polygon_geojson)
    assert result == expected_esri_json


def test_geojson_to_esri_json_multipolygon():
    # Test if geojson_to_esri_json correctly converts a GeoJSON MultiPolygon to ESRI JSON
    multipolygon_geojson = {
        "type": "MultiPolygon",
        "coordinates": [
            [
                [
                    [3.2707, 6.4605],
                    [3.2707, 6.6403],
                    [3.6004, 6.6403],
                    [3.6004, 6.4605],
                    [3.2707, 6.4605],
                ]
            ]
        ],
    }
    expected_esri_json = {
        "rings": [
            [
                [3.2707, 6.4605],
                [3.2707, 6.6403],
                [3.6004, 6.6403],
                [3.6004, 6.4605],
                [3.2707, 6.4605],
            ]
        ]
    }
    result = GeodataUtils.geojson_to_esri_json(multipolygon_geojson)
    assert result == expected_esri_json


def test_geojson_to_esri_json_unsupported_type():
    # Test if geojson_to_esri_json raises an error for unsupported types
    unsupported_geojson = {"type": "UnsupportedType", "coordinates": []}
    with pytest.raises(
        ValueError, match="Unsupported GeoJSON geometry type: UnsupportedType"
    ):
        GeodataUtils.geojson_to_esri_json(unsupported_geojson)


# test CheckDependencies


def test_pandas_installed():
    # Mock the successful import of pandas
    with patch(
        "nigeria_geodata.utils.common.CheckDependencies.pandas", create=True
    ) as mock_pandas:
        mock_pandas = mock_pandas.return_value
        result = CheckDependencies.pandas()
        assert result == mock_pandas


def test_pandas_not_installed():
    # Simulate pandas not being installed and throwing ImportError
    with patch("builtins.__import__", side_effect=PackageNotFoundError):
        with pytest.raises(
            PackageNotFoundError,
            match="pandas is required for rendering results as a dataframe",
        ):
            CheckDependencies.pandas()


def test_geopandas_installed():
    # Mock the successful import of geopandas
    with patch(
        "nigeria_geodata.utils.common.CheckDependencies.geopandas", create=True
    ) as mock_geopandas:
        mock_geopandas = mock_geopandas.return_value
        result = CheckDependencies.geopandas()
        assert result == mock_geopandas


def test_geopandas_not_installed():
    # Simulate geopandas not being installed and throwing ImportError
    with patch("builtins.__import__", side_effect=PackageNotFoundError):
        with pytest.raises(
            PackageNotFoundError,
            match="geopandas is required for rendering results as a geodataframe",
        ):
            CheckDependencies.geopandas()


def test_typer_installed():
    # Mock the successful import of typer
    with patch(
        "nigeria_geodata.utils.common.CheckDependencies.typer", create=True
    ) as mock_typer:
        mock_typer = mock_typer.return_value
        result = CheckDependencies.typer()
        assert result == mock_typer


def test_typer_not_installed():
    # Simulate typer not being installed and throwing ImportError
    with patch("builtins.__import__", side_effect=PackageNotFoundError):
        with pytest.raises(
            PackageNotFoundError, match="typer is required for CLI support"
        ):
            CheckDependencies.typer()


def test_lonboard_installed():
    # Mock the successful import of lonboard.viz
    with patch(
        "nigeria_geodata.utils.common.CheckDependencies.lonboard", create=True
    ) as mock_lonboard:
        mock_lonboard = mock_lonboard.return_value
        result = CheckDependencies.lonboard()
        assert result == mock_lonboard


def test_lonboard_not_installed():
    # Simulate lonboard not being installed and throwing ImportError
    with patch("builtins.__import__", side_effect=PackageNotFoundError):
        with pytest.raises(
            ImportError, match="lonboard is required for map visualization"
        ):
            CheckDependencies.lonboard()


# test timestamp_to_datetime


def test_timestamp_to_datetime():
    timestamp_ms = 1652196544489

    # Expected datetime
    expected_datetime = "2022-05-10 17:29:04.489000"

    result = timestamp_to_datetime(timestamp_ms)

    assert str(result) == expected_datetime


# test configure_logging


def test_configure_logging():
    # Test with logging.DEBUG level
    configure_logging(logging.DEBUG)

    # Check if logger's level is set to DEBUG
    assert logger.level == logging.DEBUG

    # Check if all handler levels are set to DEBUG
    for handler in logger.handlers:
        assert handler.level == logging.DEBUG

    # Test with logging.ERROR level
    configure_logging(logging.ERROR)

    # Check if logger's level is set to ERROR
    assert logger.level == logging.ERROR

    # Check if all handler levels are set to ERROR
    for handler in logger.handlers:
        assert handler.level == logging.ERROR
