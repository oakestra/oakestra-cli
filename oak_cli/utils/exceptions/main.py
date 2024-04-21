from dataclasses import dataclass, field
from http import HTTPStatus

from oak_cli.utils.exceptions.types import OakCLIExceptionTypes


# Note: Pydantic.BaseModel and Exception do not seem to work well if inherited together.
@dataclass
class OakCLIException(Exception):
    oak_cli_exception_type: OakCLIExceptionTypes
    text: str
    http_status: HTTPStatus = None

    message: str = field(init=False)

    def __post_init__(self) -> None:
        self.message = f"'{self.oak_cli_exception_type}' exception occured: {self.text}"
