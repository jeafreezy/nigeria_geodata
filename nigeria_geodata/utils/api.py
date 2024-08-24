"""
API module for nigeria_geodata.

This module handles HTTP requests to external services, particularly those involving
geodata sources for Nigeria. It supports both GET and POST requests and includes
custom exception handling for request errors, HTTP status errors, and JSON decoding errors.

Authors:
    Emmanuel Jolaiya
    Samuel Adedoyin

Date:
    24/08/2024

Modules:
    - `make_request`: Sends HTTP requests (GET or POST) to specified service URLs.

Dependencies:
    - httpx: Used for handling asynchronous HTTP requests.
    - logger: For logging request and response details.
    - enums: Provides enumerations for request methods (GET, POST).
    - exceptions: Custom exception handling for errors such as request failures, HTTP errors, and JSON decoding issues.
"""

import json
from typing import Any, Dict
import httpx
from nigeria_geodata.utils import logger

from nigeria_geodata.utils.enums import RequestMethod
from nigeria_geodata.utils.exceptions import (
    RequestError,
    HTTPStatusError,
    JSONDecodeError,
)


def get_headers() -> Dict[str, str]:
    from nigeria_geodata import __version__

    return {"user-agent": f"nigeria_geodata/v-{__version__}"}


def make_request(
    service_url: str,
    params: Dict[str, str] = {},
    method: RequestMethod = RequestMethod.GET,
) -> Dict[str, Any]:
    """
    Sends an HTTP request to a specified service URL and handles the response.

    Args:
        service_url (str): The URL of the service to which the request will be sent.
        params (Dict[str, str], optional): A dictionary of parameters to include in the request.
                                           Defaults to an empty dictionary.
        method (RequestMethod, optional): The HTTP request method (GET or POST).
                                          Defaults to RequestMethod.GET.

    Returns:
        Dict[str, Any]: The JSON response data as a Python dictionary.

    Raises:
        RequestError: If an error occurs while making the HTTP request.
        HTTPStatusError: If the server responds with a non-2xx status code.
        JSONDecodeError: If the response cannot be parsed as valid JSON.

    Example:
        >>> make_request("https://example.com/api", {"q": "search_term"})
        {'result': 'some_data'}

    Notes:
        - The function uses `httpx.Client` to send HTTP requests.
        - The request method can be GET or POST, based on the `RequestMethod` enum.
        - In case of an error, custom exceptions are raised with informative messages.
    """
    try:
        headers = get_headers()
        with httpx.Client() as client:
            logger.info(f"Making {method.value} request to: {service_url}")
            logger.info(f"Request parameters: {params}")
            logger.info(f"Request headers: {headers}")
            if method == RequestMethod.GET:
                response = client.get(service_url, headers=headers, params=params)
            elif method == RequestMethod.POST:
                response = client.post(service_url, headers=headers, data=params)
            response.raise_for_status()
            logger.info("API request successful.")
            return response.json()
    except httpx.RequestError as exc:
        msg = f"An error occurred while requesting {exc.request.url!r}: {exc}"
        logger.error(msg)
        raise RequestError(msg) from exc
    except httpx.HTTPStatusError as exc:
        msg = f"Error response {exc.response.status_code} while requesting {exc.request.url!r}: {exc}"
        logger.error(msg)
        raise HTTPStatusError(msg) from exc
    except json.JSONDecodeError as exc:
        msg = f"Error decoding JSON response: {exc}"
        logger.error(msg)
        raise JSONDecodeError(msg) from exc
