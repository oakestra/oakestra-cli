import pathlib

import typer

from oak_cli.configuration.auxiliary import ConfigKey
from oak_cli.configuration.common import (
    check_and_handle_config_file,
    get_config_value,
    handle_missing_key_access_attempt,
    update_config_value,
)
from oak_cli.utils.typer_augmentations import AliasGroup

app = typer.Typer(cls=AliasGroup)


class CoreVar(ConfigKey):
    SYSTEM_MANAGER_IP = "system_manager_ip"

    CLUSTER_MANAGER_IP = "cluster_manager_ip"
    CLUSTER_NAME = "cluster_name"
    CLUSTER_LOCATION = "cluster_location"


def get_core_var_from_config(core_var: CoreVar) -> pathlib.Path:
    check_and_handle_config_file()
    config_string = get_config_value(key=core_var)
    handle_missing_key_access_attempt(config_string_key=config_string)
    return pathlib.Path(config_string)


@app.command(
    "configure",
    help="Configure a core variable.",
)
def configure_core_var(core_var_type: CoreVar, core_var_value: str) -> None:
    check_and_handle_config_file()
    update_config_value(key=core_var_type, value=core_var_value)
