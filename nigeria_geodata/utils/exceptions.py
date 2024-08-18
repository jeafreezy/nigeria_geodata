"""

Exceptions for nigeria_geodata

Authors:

Date:

"""


class NigeriaGeodataError(Exception):
    """Base exception for all nigeria_geodata errors."""

    pass


class RequestError(NigeriaGeodataError):
    """Exception raised for errors during the request."""

    pass


class HTTPStatusError(NigeriaGeodataError):
    """Exception raised for HTTP status errors."""

    pass


class JSONDecodeError(NigeriaGeodataError):
    """Exception raised for JSON decoding errors."""

    pass


class PackageNotFoundError(ModuleNotFoundError):
    """Exception raised when required packages are not found."""

    pass
