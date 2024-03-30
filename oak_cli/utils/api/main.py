import json
import sys
from http import HTTPStatus
from typing import NamedTuple, Optional, Tuple, Union

import requests

from oak_cli.utils.api.common import HttpMethod
from oak_cli.utils.api.login import get_login_token
from oak_cli.utils.logging import logger


class ApiQueryComponents(NamedTuple):
    url: str
    headers: dict
    data: dict = None


def _prepare_api_query_components(
    base_url: str,
    api_endpoint: str = None,
    custom_headers: dict = None,
    data: dict = None,
    query_params: str = None,
) -> ApiQueryComponents:
    url = base_url
    if api_endpoint is not None:
        url = f"{base_url}{api_endpoint}"
    if query_params is not None:
        url += f"?{query_params}"
    headers = custom_headers or {"Authorization": f"Bearer {get_login_token()}"}
    if data and not custom_headers:
        headers["Content-Type"] = "application/json"
    return ApiQueryComponents(url, headers, data)


def _create_failure_msg(
    what_should_happen: str,
    http_method: HttpMethod,
    url: str,
    response_status: HTTPStatus = None,
) -> str:
    return (
        " ".join(
            (
                what_should_happen,
                "request failed with",
                str(response_status),
                f"for '{http_method}' '{url}",
            )
        ),
    )


def handle_request(
    base_url: str,
    what_should_happen: str,
    http_method: HttpMethod = HttpMethod.GET,
    api_endpoint: str = None,
    headers: dict = None,
    data: dict = None,
    show_msg_on_success: bool = False,
    special_msg_on_fail: str = None,
    query_params: str = None,
    terminate_when_failed: bool = True,
) -> Union[HTTPStatus, Tuple[HTTPStatus, Optional[dict]]]:

    url, headers, data = _prepare_api_query_components(
        base_url, api_endpoint, headers, data, query_params
    )
    args = {
        "url": url,
        "verify": False,
        **({"headers": headers} if headers else {}),
        **({"json": data} if data else {}),
    }

    try:
        response = http_method.call(**args)
        response_status = HTTPStatus(response.status_code)

        if response_status == HTTPStatus.OK:
            if show_msg_on_success:
                logger.info(f"Success: {what_should_happen}")

            response = response.json()
            if isinstance(response, str):
                response = json.loads(response)
            if terminate_when_failed:
                return response
            return response_status, response
        else:
            logger.error(f"FAILED: {special_msg_on_fail or what_should_happen}!")
            logger.error(_create_failure_msg(what_should_happen, http_method, url, response_status))
            logger.error(f"response: '{response}'")
            if terminate_when_failed:
                sys.exit(1)
            return response_status, None

    except requests.exceptions.RequestException as e:
        logger.error(_create_failure_msg(what_should_happen, http_method, url))
        logger.error(e)
        if terminate_when_failed:
            sys.exit(1)
        return HTTPStatus.INTERNAL_SERVER_ERROR, None
