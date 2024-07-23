from typing import List
from nigeria_geodata.models.common import DataSourceInfo


class DataSource:
    """
    Class for managing the metadata of the supported data sources.
    """

    GRID3 = DataSourceInfo(
        name="GRID3",
        url="https://grid3.org/",
        description=(
            "GRID3 has country-wide data available for Nigeria, in collaboration with "
            "our partners CIESIN at Columbia University and WorldPop at the University of Southampton. "
            "Our data includes population estimates, settlements, subnational boundaries, and critical infrastructure."
        ),
    )
    NGSA = DataSourceInfo(
        name="NGSA",
        url="https://ngsa.gov.ng/",
        description=("Nigeria Geological Survey Agency"),
    )

    @classmethod
    def list_sources(cls) -> List[DataSourceInfo]:
        """Return a list of all data source details."""
        return [cls.GRID3]
