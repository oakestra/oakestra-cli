import pathlib
import readline

from oak_cli.configuration.common import get_config_value
from oak_cli.configuration.keys.enums import ConfigurableConfigKey
from oak_cli.utils.logging import logger


def prompt_for_path(path_name: str) -> pathlib.Path:
    while True:
        logger.info(f"Please provide the '{path_name}'")
        # https://stackoverflow.com/questions/56119177/how-to-make-a-python-script-tab-complete-directories-in-terminal/56119373#56119373
        readline.set_completer_delims(" \t\n=")
        readline.parse_and_bind("tab: complete")
        user_typed_path = pathlib.Path(input("Enter Path (tab complete support): "))
        if not user_typed_path.exists():
            logger.error("No file was found for the provided path!")
            continue
        break
    return user_typed_path


def get_main_oak_repo_path() -> pathlib.Path:
    return pathlib.Path(get_config_value(ConfigurableConfigKey.MAIN_OAK_REPO_PATH))
