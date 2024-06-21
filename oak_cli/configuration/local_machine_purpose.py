import typer

from oak_cli.configuration.auxiliary import ConfigKey
from oak_cli.configuration.common import (
    check_and_handle_config_file,
    configure_aspect,
    get_config_value,
)
from oak_cli.utils.typer_augmentations import AliasGroup
from oak_cli.utils.types import CustomEnum

app = typer.Typer(cls=AliasGroup)


class LocalMachinePurpose(CustomEnum):
    """A machine can have one, multiple, or all of these purposes."""

    ROOT_ORCHESTRATOR = "root_orchestrator"
    CLUSTER_ORCHESTRATOR = "cluster_orchestrator"
    WORKER_NODE = "worker_node"


def get_local_machine_purpose_from_config() -> LocalMachinePurpose:
    check_and_handle_config_file()
    return LocalMachinePurpose(get_config_value(ConfigKey.LOCAL_MACHINE_PURPOSE_KEY))


@app.command(
    "configure",
    help="Configure the purpose of the local machine w.r.t. Oakestra.",
)
def configure_local_machine_purpose() -> None:
    check_and_handle_config_file()
    configure_aspect(
        aspect=LocalMachinePurpose,
        configuration_text="local machine purpose",
        config_key=ConfigKey.LOCAL_MACHINE_PURPOSE_KEY,
    )
