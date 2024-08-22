"""

Async core implementation module.

Authors:

Date:

"""

import abc


class AsyncBaseDataSource(metaclass=abc.ABCMeta):
    """
    AsyncBaseData Factory.

    Async Abstract Base Class which defines most inputs and methods used by the geo data source.

    """

    @abc.abstractmethod
    async def list_data(self):
        """Provides an interface to list all available data from the data source."""
        raise NotImplementedError

    @abc.abstractmethod
    async def search(self):
        """Provides an interface to search for available data from the data source."""
        raise NotImplementedError

    @abc.abstractmethod
    async def filter(self):
        """Provides an interface to filter data from the data source."""
        raise NotImplementedError

    def __repr__(self) -> str:
        return "<AsyncBaseDataFactory>"
