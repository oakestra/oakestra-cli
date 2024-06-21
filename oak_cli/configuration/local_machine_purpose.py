import json
from typing import List

import typer

from oak_cli.configuration.auxiliary import ConfigKey
from oak_cli.configuration.common import (
    check_and_handle_config_file,
    get_config_value,
    handle_missing_key_access_attempt,
    update_config_value,
)
from oak_cli.utils.logging import logger
from oak_cli.utils.typer_augmentations import AliasGroup
from oak_cli.utils.types import CustomEnum

app = typer.Typer(cls=AliasGroup)


class LocalMachinePurpose(CustomEnum):
    """A machine can have one, multiple, or all of these purposes."""

    ROOT_ORCHESTRATOR = "root_orchestrator"
    CLUSTER_ORCHESTRATOR = "cluster_orchestrator"
    WORKER_NODE = "worker_node"


def get_local_machine_purposes_from_config() -> List[LocalMachinePurpose]:
    check_and_handle_config_file()
    config_json_string = get_config_value(ConfigKey.LOCAL_MACHINE_PURPOSE_KEY)
    handle_missing_key_access_attempt(
        config_string_key=config_json_string,
        what_should_be_found="local machine purpose",
        configuration_cmd="oak c local-machine-purpose configure",
    )
    config_list = json.loads(config_json_string)
    return [LocalMachinePurpose(purpose_name) for purpose_name in config_list]


@app.command(
    "configure",
    help="Configure the purpose of the local machine w.r.t. Oakestra.",
)
def configure_local_machine_purpose(
    # NOTE: Sets are not yet supported by the frameworks.
    local_machine_purposes: List[LocalMachinePurpose],
) -> None:
    local_machine_purposes = set(local_machine_purposes)
    check_and_handle_config_file()
    update_config_value(
        key=ConfigKey.LOCAL_MACHINE_PURPOSE_KEY,
        # NOTE: The config only supports strings.
        value=json.dumps([purpose.value for purpose in local_machine_purposes]),
    )
