import pathlib

from oak_cli.addons.flops.SLAs.common import FLOpsSLAs


class FLOpsMockDataProviderSLAs(FLOpsSLAs):
    MNIST_SIMPLE = "mnist_simple"
    MNIST_MULTI = "mnist_multi"

    CIFAR10_SIMPLE = "cifar10_simple"

    # Note: This should be refactored and placed in the common parent class.
    @classmethod
    def get_SLAs_path(cls) -> pathlib.Path:
        return pathlib.Path(__file__).resolve().parent
