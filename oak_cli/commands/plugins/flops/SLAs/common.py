import pathlib

from oak_cli.utils.types import CustomEnum


def get_FLOps_SLAs_path() -> pathlib.Path:
    return pathlib.Path(__file__).resolve().parent


class FLOpsSLAs(CustomEnum):
    CIFAR10_KERAS = "cifar10_keras"
    CIFAR10_PYTORCH = "cifar10_pytorch"
