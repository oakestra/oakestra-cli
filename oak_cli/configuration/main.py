from typing import List, Optional

import typer
from rich import print_json
from typing_extensions import Annotated

import oak_cli.configuration.keys.main
import oak_cli.configuration.local_machine_purpose.main
import oak_cli.docker.cluster_orchestrator
import oak_cli.docker.root_orchestrator
from oak_cli.configuration.common import (
    OAK_CLI_CONFIG_PATH,
    check_and_handle_config_file,
    open_local_config,
)
from oak_cli.configuration.local_machine_purpose.enum import LocalMachinePurpose
from oak_cli.configuration.local_machine_purpose.main import set_local_machine_purposes
from oak_cli.utils.common import clear_file
from oak_cli.utils.typer_augmentations import AliasGroup

app = typer.Typer(cls=AliasGroup)


@app.command(
    "local-machine-purpose, l",
    help=(
        "Configure the purpose of the local machine w.r.t. Oakestra.\n"
        "Specify one or multiple purposes at once.\n"
        "E.g. ... --purpose A --purpose B\n| "
        "For further information run 'oak explain local-machine-purpose'"
    ),
)
def configure_local_machine_purpose(
    # NOTE: Sets are not yet supported by the frameworks.
    # local_machine_purposes: Optional[List[LocalMachinePurpose]] = None,
    local_machine_purposes: Annotated[
        Optional[List[LocalMachinePurpose]],
        typer.Option("--purpose", help="A local machine purposes."),
    ] = None,
) -> None:
    if local_machine_purposes:
        set_local_machine_purposes(set(local_machine_purposes))
        return

    if typer.confirm(
        "Do you want to use all OAK-CLI capabilities?\n"
        "(NOTE: All features at once are only usable on a monolith system"
        " that hosts all Oakestra components.)"
    ):
        set_local_machine_purposes(set([LocalMachinePurpose.EVERYTHING]))
        return

    if typer.confirm("Do you want to use the default initial capabilities?"):
        set_local_machine_purposes(set([LocalMachinePurpose.INITIAL]))
        return

    requested_purposes = []
    is_monolith = typer.confirm(
        "Do you intend to use Oakestra only on this single machine? (Monolith)"
    )

    if is_monolith:
        requested_purposes.extend(
            [
                LocalMachinePurpose.ROOT_ORCHESTRATOR,
                LocalMachinePurpose.CLUSTER_ORCHESTRATOR,
                LocalMachinePurpose.WORKER_NODE,
            ]
        )
    else:
        if typer.confirm("Does your local machine host Oakestra's Root Orchestrator?"):
            requested_purposes.append(LocalMachinePurpose.ROOT_ORCHESTRATOR)

        if typer.confirm("Does your local machine host Oakestra's Cluster Orchestrator?"):
            requested_purposes.append(LocalMachinePurpose.CLUSTER_ORCHESTRATOR)

        if typer.confirm("Is your local machine an Oakestra's Worker Node?"):
            requested_purposes.append(LocalMachinePurpose.WORKER_NODE)

    if typer.confirm("Do you want to use Oakestra Addons?"):
        requested_purposes.append(LocalMachinePurpose.ADDON_SUPPORT)

    if typer.confirm("Are you an Oakestra Contributor/Developer?"):
        requested_purposes.append(LocalMachinePurpose.DEVELOPMENT)

    set_local_machine_purposes(set(requested_purposes))


app.add_typer(
    typer_instance=oak_cli.configuration.keys.main.app,
    name="key-vars, k",
    help="Configure OAK-CLI Key Variables",
)


@app.command("show-config, s", help="Show the current OAK-CLI configuration")
def show_config():
    check_and_handle_config_file()
    config = open_local_config()
    for section in config.sections():
        print_json(data=dict(config.items(section)))


@app.command("reset-config", help="Reset the current OAK-CLI configuration to its initial state")
def reset_config():
    clear_file(OAK_CLI_CONFIG_PATH)
    check_and_handle_config_file()
