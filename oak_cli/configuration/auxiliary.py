import pathlib
import readline

from oak_cli.utils.logging import logger
from oak_cli.utils.types import CustomEnum


class ConfigKey(CustomEnum):
    CONFIG_MAIN_KEY = "OAK_CLI"
    CONFIG_VERSION_KEY = "config_version"

    LOCAL_MACHINE_PURPOSE_KEY = "local_machine_purpose"

    MAIN_OAK_REPO_PATH_KEY = "main_oak_repo_path"
    FLOPS_REPO_PATH_KEY = "flops_repo_path"


def prompt_for_path(path_name: str) -> pathlib.Path:
    while True:
        logger.info(f"Please provide the path to {path_name}")
        # https://stackoverflow.com/questions/56119177/how-to-make-a-python-script-tab-complete-directories-in-terminal/56119373#56119373
        readline.set_completer_delims(" \t\n=")
        readline.parse_and_bind("tab: complete")
        user_typed_path = pathlib.Path(input("Enter Path (tab complete support): "))
        if not user_typed_path.exists():
            logger.error("No file was found for the provided path!")
            continue
        break
    return user_typed_path
