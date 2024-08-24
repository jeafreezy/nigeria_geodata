"""
Exceptions for the nigeria_geodata Package

This module defines custom exceptions used within the `nigeria_geodata` package.
These exceptions provide more specific error handling for various failure scenarios
that can occur during operations related to geospatial data processing and interactions.

Authors:
    Emmanuel Jolaiya
    Samuel Adedoyin

Date:
    24/08/2024

Exceptions:
    NigeriaGeodataError: Base exception for all exceptions in the nigeria_geodata package.
    RequestError: Raised for errors encountered during HTTP requests.
    HTTPStatusError: Raised for HTTP status-related errors.
    JSONDecodeError: Raised for errors encountered while decoding JSON data.
    PackageNotFoundError: Raised when a required package is not found.

"""


class NigeriaGeodataError(Exception):
    """Base exception for all nigeria_geodata errors."""

    pass


class RequestError(NigeriaGeodataError):
    """Exception raised for errors during the request.

    This exception is used to indicate problems that occur during the process
    of making requests to data sources. It may be raised due to network issues,
    invalid request parameters, or other request-related failures.
    """

    pass


class HTTPStatusError(NigeriaGeodataError):
    """Exception raised for HTTP status errors.

    This exception is used when the server returns an HTTP status code that indicates
    an error (e.g., 4xx or 5xx codes). It helps to differentiate between successful
    and unsuccessful HTTP responses.
    """

    pass


class JSONDecodeError(NigeriaGeodataError):
    """Exception raised for JSON decoding errors.

    This exception is raised when there are issues decoding JSON data. It may be caused
    by malformed JSON, unexpected data formats, or other issues related to JSON processing.
    """

    pass


class PackageNotFoundError(ModuleNotFoundError):
    """Exception raised when required packages are not found.

    This exception is raised when a required third-party package or module is not found
    or not installed. It helps in identifying and handling missing dependencies.
    """

    pass
