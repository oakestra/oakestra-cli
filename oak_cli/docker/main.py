import typer

import oak_cli.docker.cluster_orchestrator
import oak_cli.docker.root_orchestrator
from oak_cli.utils.typer_augmentations import typer_help_text

app = typer.Typer(
    help=typer_help_text("docker ALEX"),
)
app.add_typer(
    typer_instance=oak_cli.docker.root_orchestrator.app,
    name="ro",
    help=typer_help_text("root-orchestrator docker-compose"),
)
app.add_typer(
    typer_instance=oak_cli.docker.cluster_orchestrator.app,
    name="co",
    help=typer_help_text("cluster-orchestrator docker-compose"),
)
