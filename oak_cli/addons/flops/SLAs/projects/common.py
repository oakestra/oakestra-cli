import pathlib

from oak_cli.addons.flops.SLAs.common import FLOpsSLAs


class FLOpsProjectSLAs(FLOpsSLAs):
    CIFAR10_KERAS = "cifar10_keras"
    CIFAR10_PYTORCH = "cifar10_pytorch"
    MNIST_SKLEARN_SMALL = "mnist_sklearn_small"
    HIERARCHICAL_MNIST_SKLEARN_SMALL = "hierarchical_mnist_sklearn_small"
    MNIST_SKLEARN_LARGE = "mnist_sklearn_large"

    # Note: This should be refactored and placed in the common parent class.
    @classmethod
    def get_SLAs_path(cls) -> pathlib.Path:
        return pathlib.Path(__file__).resolve().parent
