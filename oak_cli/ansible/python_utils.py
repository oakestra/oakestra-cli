import enum
import pathlib
from typing import Union

from oak_cli.utils.common import get_oak_cli_path

CLI_ANSIBLE_PATH = get_oak_cli_path() / "ansible"

CLI_PLAYBOOKS_PATH = CLI_ANSIBLE_PATH / "playbooks"


class CliPlaybook(enum.Enum):
    INSTALL_FUNDAMENTALS = "install_fundamentals"

    def get_path(self, as_string: bool = True) -> Union[str, pathlib.Path]:
        path = CLI_PLAYBOOKS_PATH / f"{self.value}.yml"
        return str(path) if as_string else path
