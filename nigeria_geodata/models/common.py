from dataclasses import dataclass
from typing import Any, List


@dataclass(frozen=True)
class DataSourceInfo:
    name: str
    url: str
    description: str


@dataclass
class EsriFeatureServiceBasicInfo:
    name: str
    url: str
    type: str


@dataclass
class EsriFeatureLayerBasicInfo:
    id: int
    name: str
    parentLayerId: int
    defaultVisibility: bool
    subLayerIds: Any
    minScale: int
    maxScale: 0
    type: str
    geometryType: str


@dataclass
class EsriFeatureLayerDetailedInfo:
    id: int
    name: str
    parentLayerId: int
    defaultVisibility: bool
    subLayerIds: Any
    minScale: int
    maxScale: 0
    type: str
    geometryType: str


@dataclass
class EsriSpatialReference:
    wkid: int
    latestWkid: int


@dataclass
class EsriFeatureServiceFullExtent:
    xmin: int
    ymin: int
    xmax: int
    ymax: int
    spatialReferemce: EsriSpatialReference


@dataclass
class EsriFeatureServiceDetailedInfo:
    """
    This model will store the important information about a feature service.
    Esri returns more objects, but the ones here are the most relevant to the package.
    """

    serviceItemId: str
    """The Id of the service."""
    serviceDescription: str
    """The description of the service."""
    maxRecordCount: int
    """The maximum number of record the service can return."""
    supportedQueryFormats: str
    """The formats in which query results can be returned."""
    supportedExportFormats: str
    """The supported export formats."""
    capabilities: str
    """The capabilitise of tshe feature server."""
    description: str
    """The long html description of the service. Usually contains the year the data was collected."""
    copyrightText: str
    """The copyright of the service."""
    spatialReference: EsriSpatialReference
    """The spatial reference system."""
    fullExtent: EsriFeatureServiceFullExtent
    """The full extent of the dataset."""
    layers: List[EsriFeatureLayerBasicInfo]
    """List of available layers in the service."""
    tables: List[Any]
    """The available tables in the service."""
