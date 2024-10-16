from __future__ import annotations

import configparser
import json
import pathlib
import sys

from oak_cli.addons.flops.SLAs.main import check_flops_folders
from oak_cli.apps.prepared_SLAs.main import check_sla_folder
from oak_cli.configuration.consts import OAK_CLI_CONFIG_PATH, OAK_CLI_USER_FOLDER_PATH
from oak_cli.configuration.keys.enums import ConfigKey, ConfigurableConfigKey, InternalConfigKey
from oak_cli.configuration.local_machine_purpose.enum import LocalMachinePurpose
from oak_cli.utils.logging import logger

OAK_CLI_SLA_FOLDER_PATH = OAK_CLI_USER_FOLDER_PATH / "SLAs"

# Version needs to be incremented every time the config structure changes.
_CONFIG_VERSION = "1"


def _check_local_config_valid() -> bool:
    if not OAK_CLI_CONFIG_PATH.is_file():
        return False

    config = open_local_config()
    if len(config.sections()) == 0:
        return False

    all_config_key_value_pairs = config.items(InternalConfigKey.CONFIG_MAIN_KEY.value)
    all_config_elements = [elem for sublist in all_config_key_value_pairs for elem in sublist]
    if InternalConfigKey.CONFIG_VERSION.value not in all_config_elements:
        return False

    local_config_version = get_config_value(InternalConfigKey.CONFIG_VERSION)
    return local_config_version == _CONFIG_VERSION


def open_local_config() -> configparser.ConfigParser:
    config = configparser.ConfigParser()
    config.read(OAK_CLI_CONFIG_PATH)
    return config


def update_config_value(key: ConfigKey, value: str) -> None:
    """NOTE: The config only supports strings."""
    config = open_local_config()
    config[InternalConfigKey.CONFIG_MAIN_KEY.value][key.value] = value  # type: ignore
    _update_config(config)


def get_config_value(key: ConfigKey, terminate_if_key_is_missing_from_conf: bool = True) -> str:
    config = open_local_config()[InternalConfigKey.CONFIG_MAIN_KEY.value]
    value_from_config = config.get(key.value, "")  # type: ignore
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
    update_config_value(key=InternalConfigKey.CONFIG_VERSION, value=_CONFIG_VERSION)
    update_config_value(
        key=ConfigurableConfigKey.LOCAL_MACHINE_PURPOSE,
        value=json.dumps([LocalMachinePurpose.INITIAL.value]),
    )
    logger.info(
        "\n".join(
            (
                "New initial un-configured config file created for OAK-CLI.",
                "It uses a minimal initial configuration.",
                "It can be displayed via 'oak c show-config'.",
                f"The config can be found at: '{OAK_CLI_CONFIG_PATH}'",
            )
        )
    )


def _check_user_oak_folder_and_content() -> None:
    if not OAK_CLI_USER_FOLDER_PATH.is_dir():
        OAK_CLI_USER_FOLDER_PATH.mkdir(exist_ok=True)

    check_sla_folder()
    check_flops_folders()


def check_and_handle_config_file() -> None:
    _check_user_oak_folder_and_content()

    if _check_local_config_valid():
        return

    logger.info("No config file found. Creating a new empty un-configured config file.")
    _create_initial_unconfigured_config_file()


def _handle_missing_key_access_attempt(key: ConfigKey) -> None:
    missing_key = key.value  # type: ignore
    logger.error(
        "\n".join(
            (
                f"The '{missing_key}' was not found in your oak-CLI config.",
                "Please first configure it by running the matching oak-cli configuration cmd.",
                f"> oak c key-vars configure {missing_key}",
            )
        )
    )
    sys.exit(1)


def get_main_oak_repo_path() -> pathlib.Path:
    config_value = get_config_value(ConfigurableConfigKey.MAIN_OAK_REPO_PATH)
    return pathlib.Path(config_value)
