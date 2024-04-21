import json
from dataclasses import dataclass, field
from http import HTTPStatus
from typing import NamedTuple

import requests

from oak_cli.utils.api.custom_http import HttpMethod
from oak_cli.utils.api.login import get_login_token
from oak_cli.utils.exceptions.main import OakCLIException
from oak_cli.utils.exceptions.types import OakCLIExceptionTypes
from oak_cli.utils.logging import logger


class RequestCore(NamedTuple):
    base_url: str
    api_endpoint: str = None
    query_params: str = None
    http_method: HttpMethod = HttpMethod.GET
    custom_headers: dict = None
    data: dict = None


class RequestAuxiliaries(NamedTuple):
    what_should_happen: str
    oak_cli_exception_type: OakCLIExceptionTypes
    show_msg_on_success: bool = False
    is_oakestra_api: bool = True


# Note: The use of Pydantic here leads to strange validation errors.
@dataclass
class CustomRequest:
    core: RequestCore
    aux: RequestAuxiliaries

    headers: dict = field(default=None, init=False)
    url: str = field(default=None, init=False)
    args: dict = field(default=None, init=False)
    response: requests.Response = field(default=None, init=False)

    def __post_init__(self):
        self._prepare()

    def _prepare(self) -> None:
        self.url = self.core.base_url
        if self.core.api_endpoint is not None:
            self.url = f"{self.core.base_url}{self.core.api_endpoint}"
        if self.core.query_params is not None:
            self.url += f"?{self.core.query_params}"

        if self.core.custom_headers:
            self.headers = self.core.custom_headers
        else:
            self.headers = (
                {"Authorization": f"Bearer {get_login_token()}"} if self.aux.is_oakestra_api else {}
            )

        if self.core.data and not self.core.custom_headers:
            self.headers["Content-Type"] = "application/json"

        self.args = {
            "url": self.url,
            "verify": False,
            **({"headers": self.headers} if self.headers else {}),
            **({"json": self.core.data} if self.core.data else {}),
        }

    def _create_failure_msg(self) -> str:
        return " ".join(
            (
                self.aux.what_should_happen,
                "request failed",
                f"with {self.response.status}" if self.response else "- no response",
                f"for '{self.core.http_method}' '{self.url}",
            )
        )

    def execute(self) -> any:
        error_msg = ""
        try:
            self.response = self.core.http_method.call(**self.args)
            self.response.status = HTTPStatus(self.response.status_code)
            if self.response.status == HTTPStatus.OK:
                if self.aux.show_msg_on_success:
                    logger.info(f"Success: '{self.aux.what_should_happen}'")
                response = self.response.json()
                if isinstance(response, str):
                    response = json.loads(response)
                return response

        except requests.exceptions.RequestException as e:
            error_msg = f"exception: {e}: "

        error_msg += self._create_failure_msg()

        raise OakCLIException(
            oak_cli_exception_type=self.aux.oak_cli_exception_type,
            text=error_msg,
            http_status=self.response.status if self.response else None,
        )
