import pathlib

from oak_cli.utils.types import CustomEnum


class FLOpsSLAs(CustomEnum):

    @classmethod
    def get_SLAs_path(cls) -> pathlib.Path:
        return pathlib.Path(__file__).resolve().parent
