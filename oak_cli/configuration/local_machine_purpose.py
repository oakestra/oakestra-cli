import json
from typing import List, Optional

import typer

from oak_cli.configuration.auxiliary import ConfigKey
from oak_cli.configuration.common import (
    check_and_handle_config_file,
    get_config_value,
    handle_missing_key_access_attempt,
    update_config_value,
)
from oak_cli.utils.typer_augmentations import AliasGroup
from oak_cli.utils.types import CustomEnum

app = typer.Typer(cls=AliasGroup)


class LocalMachinePurpose(CustomEnum):
    """A machine can have one, multiple, or all of these purposes."""

    ROOT_ORCHESTRATOR = "root_orchestrator"
    CLUSTER_ORCHESTRATOR = "cluster_orchestrator"
    WORKER_NODE = "worker_node"


def get_local_machine_purposes_from_config(
    terminate_if_key_is_missing_from_conf: bool = True,
) -> Optional[List[LocalMachinePurpose]]:
    check_and_handle_config_file()
    config_json_string = get_config_value(ConfigKey.LOCAL_MACHINE_PURPOSE_KEY)
    if terminate_if_key_is_missing_from_conf:
        handle_missing_key_access_attempt(
            config_string_key=config_json_string,
            what_should_be_found="local machine purpose",
            configuration_cmd="oak c local-machine-purpose configure",
        )
    else:
        if not config_json_string:
            return
    config_list = json.loads(config_json_string)
    return [LocalMachinePurpose(purpose_name) for purpose_name in config_list]


def check_if_local_machine_has_required_purposes(
    required_purposes: List[LocalMachinePurpose],
) -> bool:
    local_machine_purposes = get_local_machine_purposes_from_config(
        terminate_if_key_is_missing_from_conf=False
    )
    if not local_machine_purposes:
        return False
    return set(local_machine_purposes).issubset(set(required_purposes))


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
