import sys
from dataclasses import dataclass, field
from http import HTTPStatus

from oak_cli.utils.exceptions.types import OakCLIExceptionTypes
from oak_cli.utils.logging import logger


# Note: Pydantic.BaseModel and Exception do not seem to work well if inherited together.
@dataclass
class OakCLIException(Exception):
    oak_cli_exception_type: OakCLIExceptionTypes
    text: str
    http_status: HTTPStatus = None

    message: str = field(init=False)

    def __post_init__(self) -> None:
        self.message = f"'{self.oak_cli_exception_type}' exception occured: {self.text}"

    def log_and_exit(self, special_message: str = None) -> None:
        logger.error(msg=special_message or self.message)
        sys.exit(1)

    def handle_exception(
        self,
        oak_cli_execption_type: OakCLIExceptionTypes,
        special_message: str = None,
    ) -> None:
        if self.oak_cli_exception_type == oak_cli_execption_type:
            if "no response" in self.message:
                self.log_and_exit(special_message or self.message)
        raise self
