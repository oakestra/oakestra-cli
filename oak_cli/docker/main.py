import typer

import oak_cli.docker.cluster_orchestrator
import oak_cli.docker.root_orchestrator
from oak_cli.configuration.local_machine_purpose import (
    LocalMachinePurpose,
    check_if_local_machine_has_required_purposes,
)
from oak_cli.utils.typer_augmentations import typer_help_text

app = typer.Typer()

if check_if_local_machine_has_required_purposes(
    required_purposes=[LocalMachinePurpose.ROOT_ORCHESTRATOR]
):
    app.add_typer(
        typer_instance=oak_cli.docker.root_orchestrator.app,
        name="ro",
        help=typer_help_text("root-orchestrator docker-compose"),
    )

if check_if_local_machine_has_required_purposes(
    required_purposes=[LocalMachinePurpose.CLUSTER_ORCHESTRATOR]
):
    app.add_typer(
        typer_instance=oak_cli.docker.cluster_orchestrator.app,
        name="co",
        help=typer_help_text("cluster-orchestrator docker-compose"),
    )
