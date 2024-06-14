import pathlib

from oak_cli.utils.common import get_oak_cli_path
from oak_cli.utils.types import CustomEnum


def get_SLAs_path() -> pathlib.Path:
    return get_oak_cli_path() / "apps" / "SLAs"


class AppSLAs(CustomEnum):
    DEFAULT = "default_app_with_services"
    BLANK = "blank_app_without_services"

    INFERENCE_TESTER_MNIST_SKLEARN = "inference_tester_mnist_sklearn"

    PYTHON = "python"
    DUMMY_TESTER = "dummy_tester"
