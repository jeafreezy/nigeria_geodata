"""
API module for nigeria_geodata
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

    return {"user-agent": f"nigeria_geodata/{__version__}"}


def make_request(
    service_url: str,
    params: Dict[str, str] = {},
    method: RequestMethod = RequestMethod.GET,
) -> Dict[str, Any]:
    """
    Handles the making of request to the datasource.
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
