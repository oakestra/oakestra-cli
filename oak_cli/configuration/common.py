import configparser
import pathlib
from typing import Any

from oak_cli.configuration.auxiliary import ConfigKey
from oak_cli.utils.logging import logger
from oak_cli.utils.types import CustomEnum

OAK_CLI_CONFIG_PATH = pathlib.Path.home() / ".oak_cli_config"

# Version needs to be incremented every time the config structure changes.
CONFIG_VERSION = "1"


def _check_local_config_valid() -> bool:
    if not OAK_CLI_CONFIG_PATH.is_file():
        return False

    config = open_local_config()
    all_config_key_value_pairs = config.items(ConfigKey.CONFIG_MAIN_KEY.value)
    all_config_elements = [elem for sublist in all_config_key_value_pairs for elem in sublist]
    if ConfigKey.CONFIG_VERSION_KEY.value not in all_config_elements:
        return False

    local_config_version = get_config_value(ConfigKey.CONFIG_VERSION_KEY)
    return local_config_version == CONFIG_VERSION


def open_local_config() -> configparser.ConfigParser:
    config = configparser.ConfigParser()
    config.read(OAK_CLI_CONFIG_PATH)
    return config


def update_config_value(key: ConfigKey, value: Any) -> None:
    config = open_local_config()
    config[ConfigKey.CONFIG_MAIN_KEY.value][key.value] = value
    _update_config(config)


def get_config_value(key: ConfigKey) -> Any:
    return open_local_config()[ConfigKey.CONFIG_MAIN_KEY.value][key.value]


def configure_aspect(
    aspect: CustomEnum,
    configuration_text: str,
    config_key: ConfigKey,
) -> None:
    options = [*aspect]
    options_info = "\n  "
    for i, option in enumerate(options):
        options_info += f"{i+1}: {option.value.upper()}\n  "
    logger.info(f"Select your preferred '{configuration_text}': {options_info}")
    while True:
        preferred_option = input("Type your preference: ").lower()
        if (
            len(preferred_option) == 1
            and preferred_option.isdigit()
            and int(preferred_option) <= len(options)
            and int(preferred_option) > 0
        ):
            preferred_option = options[int(preferred_option) - 1]
        elif preferred_option in [option.value for option in options]:
            preferred_option = aspect(preferred_option)
        else:
            logger.info("Please only type one of the available options.")
            continue
        break

    update_config_value(key=config_key, value=str(preferred_option).lower())


def _update_config(config: configparser.ConfigParser) -> None:
    with open(OAK_CLI_CONFIG_PATH, "w") as config_file:
        config.write(config_file)


def _create_initial_unconfigured_config_file() -> None:
    if not OAK_CLI_CONFIG_PATH.exists():
        OAK_CLI_CONFIG_PATH.touch()

    config = configparser.ConfigParser()
    config[ConfigKey.CONFIG_MAIN_KEY.value] = {}
    config = update_config_value(
        config=config, key=ConfigKey.CONFIG_VERSION_KEY, value=CONFIG_VERSION
    )
    logger.info(
        "\n".join(
            (
                "New initial un-configured config file created for OAK-CLI.",
                f"The config can be found at: '{OAK_CLI_CONFIG_PATH}'",
            )
        )
    )


def check_and_handle_config_file() -> None:
    if _check_local_config_valid():
        return

    logger.info("No config file found. Creating a new empty un-configured config file.")
    _create_initial_unconfigured_config_file()
