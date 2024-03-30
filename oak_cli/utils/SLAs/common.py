import pathlib

from oak_cli.utils.common import get_oak_cli_path
from oak_cli.utils.types import CustomEnum


def get_SLAs_path() -> pathlib.Path:
    return get_oak_cli_path() / "utils" / "SLAs"


class KnownSLA(CustomEnum):
    DEFAULT = "default_app_with_services"
    BLANK = "blank_app_without_services"
    FL = "fl_app"
    BUILDER = "builder"
    ENDLESS_BUILDER = "endless_builder"
    ENDLESS_CONDA = "endless_conda"
    ENDLESS_NET = "endless_net"
    ENDLESS_FLUI = "endless_flui"
    FLUI = "flui"
    SINGLE_SERVICE = "single_service"
