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
        """Provides an interface to search for available data from the inheriting data source."""
        raise NotImplementedError

    @abc.abstractmethod
    def get_data(self):
        """Provides an interface to download available data from the inheriting data source."""
        raise NotImplementedError

    def __repr__(self) -> str:
        return "<SyncBaseDataFactory>"


class ASyncBaseDataSource(metaclass=abc.ABCMeta):
    """
    BaseData Factory.

    Abstract Base Class which defines most inputs and methods used by the geo data source.

    """

    @abc.abstractmethod
    async def list_data(self):
        """Provides an async interface to list all available data from the data source."""
        raise NotImplementedError

    @abc.abstractmethod
    async def search(self):
        """Provides an async interface to search for available data from the inheriting data source."""
        raise NotImplementedError

    @abc.abstractmethod
    async def download(self):
        """Provides an async interface to download available data from the inheriting data source."""
        raise NotImplementedError

    @abc.abstractmethod
    async def export(self):
        """Provides an async interface to export data into different formats."""
        raise NotImplementedError

    def __repr__(self) -> str:
        return "<AsyncBaseDataFactory>"
