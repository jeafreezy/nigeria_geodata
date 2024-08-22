"""

Core implementation module.

Authors:

Date:

"""

import abc


class SyncBaseDataSource(metaclass=abc.ABCMeta):
    """
    BaseData Factory.

    Abstract Base Class which defines most inputs and methods used by the geo data source.

    """

    @abc.abstractmethod
    def list_data(self):
        """Provides an interface to list all available data from the data source."""
        raise NotImplementedError

    @abc.abstractmethod
    def search(self):
        """Provides an interface to search for available data from the data source."""
        raise NotImplementedError

    @abc.abstractmethod
    def filter(self):
        """Provides an interface to filter data from the data source."""
        raise NotImplementedError

    def __repr__(self) -> str:
        return "<SyncBaseDataFactory>"
