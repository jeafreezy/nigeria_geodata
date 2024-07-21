from dataclasses import dataclass, field
from typing import List, Dict, Union, Any


@dataclass(frozen=True)
class DataSourceInfo:
    name: str
    url: str
    description: str


@dataclass
class EsriFeatureServiceBasicInfo:
    name: str
    url: Union[str, None] = None
    type: Union[str, None] = None


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
class EsriGeometryBbox:
    xmin: int
    ymin: int
    xmax: int
    ymax: int


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
    featureServerURL: str
    """The feature server URL"""


@dataclass
class Geometry:
    type: str
    coordinates: Union[
        List[float],
        List[List[float]],
        List[List[List[float]]],
        List[List[List[List[float]]]],
    ]


@dataclass
class Feature:
    type: str = "Feature"
    geometry: Geometry = None
    properties: Dict[str, Any] = field(default_factory=dict)


# FeatureCollection Dataclass
@dataclass
class FeatureCollection:
    type: str = "FeatureCollection"
    features: List[Feature] = field(default_factory=list)
