import pathlib

from oak_cli.commands.plugins.flops.SLAs.common import FLOpsSLAs


class FLOpsMockDataProviderSLAs(FLOpsSLAs):
    MNIST_SIMPLE = "mnist_simple"

    # Note: This should be refactored and placed in the common parent class.
    @classmethod
    def get_SLAs_path(cls) -> pathlib.Path:
        return pathlib.Path(__file__).resolve().parent
