"""

Grid3 implementation module.

Authors:

Date:

"""

from nigeria_geodata.core import BaseDataFactory
from nigeria_geodata.settings import DATA_SOURCES


class Grid3Data(BaseDataFactory):
    service_url: str = DATA_SOURCES["GRID3"]["BASE_ENDPOINT"]

    def search(self, preview: bool = False):
        # search for available data by text, state, lga, ea
        # e.g how many grid3 data exists for lagos state.
        # the result will be an array of the results.
        # we can allow a variable like preview=True or false, which can allow the
        # users to preview the data on a map, or as an image like a thumbnail in jupyter notebook.
        return super().search()

    def __repr__(self) -> str:
        return "<Grid3Data>"
