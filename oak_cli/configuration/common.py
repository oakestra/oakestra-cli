from __future__ import annotations

import configparser
import pathlib
import sys
from typing import Any, Optional

from oak_cli.configuration.keys.enums import ConfigKey, InternalConfigKey
from oak_cli.utils.logging import logger

OAK_CLI_CONFIG_PATH = pathlib.Path.home() / ".oak_cli_config"

# Version needs to be incremented every time the config structure changes.
CONFIG_VERSION = "1"


def _check_local_config_valid() -> bool:
    if not OAK_CLI_CONFIG_PATH.is_file():
        return False

    config = open_local_config()
    all_config_key_value_pairs = config.items(InternalConfigKey.CONFIG_MAIN_KEY.value)
    all_config_elements = [elem for sublist in all_config_key_value_pairs for elem in sublist]
    if InternalConfigKey.CONFIG_VERSION.value not in all_config_elements:
        return False

    local_config_version = get_config_value(InternalConfigKey.CONFIG_VERSION)
    return local_config_version == CONFIG_VERSION


def open_local_config() -> configparser.ConfigParser:
    config = configparser.ConfigParser()
    config.read(OAK_CLI_CONFIG_PATH)
    return config


def update_config_value(key: ConfigKey, value: Any) -> None:
    config = open_local_config()
    config[InternalConfigKey.CONFIG_MAIN_KEY.value][key.value] = value
    _update_config(config)


def get_config_value(
    key: ConfigKey, terminate_if_key_is_missing_from_conf: bool = True
) -> Optional[str]:
    value_from_config = open_local_config()[InternalConfigKey.CONFIG_MAIN_KEY.value].get(key.value)
    if not value_from_config and terminate_if_key_is_missing_from_conf:
        _handle_missing_key_access_attempt(key)
    return value_from_config


def _update_config(config: configparser.ConfigParser) -> None:
    with open(OAK_CLI_CONFIG_PATH, "w") as config_file:
        config.write(config_file)


def _create_initial_unconfigured_config_file() -> None:
    if not OAK_CLI_CONFIG_PATH.exists():
        OAK_CLI_CONFIG_PATH.touch()

    config = configparser.ConfigParser()
    config[InternalConfigKey.CONFIG_MAIN_KEY.value] = {}
    _update_config(config=config)
    update_config_value(key=InternalConfigKey.CONFIG_VERSION, value=CONFIG_VERSION)
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


def _handle_missing_key_access_attempt(key: ConfigKey) -> None:
    logger.error(
        "\n".join(
            (
                f"The '{key.value.replace('_', ' ')}' was not found in your oak-CLI config.",
                "Please first configure it by running the matching oak-cli configuration cmd.",
            )
        )
    )
    sys.exit(1)
