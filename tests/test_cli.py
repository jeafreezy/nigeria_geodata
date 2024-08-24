from unittest.mock import patch
from typer.testing import CliRunner
from nigeria_geodata.cli import app
from nigeria_geodata.datasources.grid3 import Grid3

runner = CliRunner()


mocked_data_list = [
    {"name": "dataset1", "url": "http://example.com/1", "type": "FeatureServer"},
    {"name": "dataset2", "url": "http://example.com/2", "type": "FeatureServer"},
]

mocked_search_results = [
    {"name": "search_result_1", "url": "http://example.com/1", "type": "FeatureServer"},
]

mocked_filter_results = [
    {"name": "filter_result_1", "url": "http://example.com/1", "type": "FeatureServer"},
]


@patch.object(Grid3, "list_data", return_value=mocked_data_list)
def test_list_data(mock_list_data):
    result = runner.invoke(app, ["grid3", "list-data", "--no-table"])

    assert result.exit_code == 0
    assert "dataset1" in result.stdout
    assert "dataset2" in result.stdout
    mock_list_data.assert_called_once_with(dataframe=False)


@patch.object(Grid3, "search", return_value=mocked_search_results)
def test_search(mock_search):
    result = runner.invoke(app, ["grid3", "search", "--query", "health"])
    assert result.exit_code == 0
    assert "search_result_1" in result.stdout
    mock_search.assert_called_once_with("health", False)


@patch.object(Grid3, "filter", return_value=mocked_filter_results)
def test_filter(mock_filter):
    bbox = "20.0,12.3,21.4,34.5"
    result = runner.invoke(
        app, ["grid3", "filter", "--data-name", "Nigeria_Health", "--bbox", bbox]
    )

    assert result.exit_code == 0
    assert "filter_result_1" in result.stdout
    mock_filter.assert_called_once_with(
        data_name="Nigeria_Health",
        state=None,
        bbox=[20.0, 12.3, 21.4, 34.5],
        aoi_geometry=None,
        preview=False,
        geodataframe=False,
    )


@patch.object(
    Grid3, "info", return_value={"name": "Nigeria_Health", "description": "Health data"}
)
def test_info(mock_info):
    result = runner.invoke(app, ["grid3", "info", "--data-name", "Nigeria_Health"])

    assert result.exit_code == 0
    assert "Nigeria_Health" in result.stdout
    assert "Health data" in result.stdout
    mock_info.assert_called_once_with("Nigeria_Health", False)


def test_docs():
    result = runner.invoke(app, ["docs"])
    assert result.exit_code == 0
    assert "Opening documentation website" in result.stdout
