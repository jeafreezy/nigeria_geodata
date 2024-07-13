"""

Core implementation module.

Authors:

Date:

"""

import abc


class BaseDataFactory(metaclass=abc.ABCMeta):
    """
    BaseData Factory.

    Abstract Base Class which defines most inputs and methods used by the geo data source.

    """

    @abc.abstractmethod
    def search(self):
        """Provides an interface to search for available data from the inheriting data source."""
        ...

    @abc.abstractmethod
    def download(self):
        """Provides an interface to download available data from the inheriting data source."""
        ...

    @abc.abstractmethod
    def export(self):
        """Provides an interface to export data into different formats."""
        ...

    def __repr__(self) -> str:
        return "<BaseDataFactory>"
