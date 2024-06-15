# NOTE: The current redundant split between the root and cluster orchestrators
# is made to natively (via typer) support their enums.
# Hopefully future typer versions will support common parent enums better.

import typer
from typing_extensions import Annotated

from oak_cli.commands.docker.aux import (
    REBUILD_APP_CMD_ALIASES,
    REBUILD_APP_CMD_HELP,
    RESTART_APP_CMD_ALIASES,
    RESTART_APP_CMD_HELP,
)
from oak_cli.commands.docker.common import rebuild_docker_compose_service, restart_docker_service
from oak_cli.commands.docker.enums import ClusterOrchestratorService
from oak_cli.utils.typer_augmentations import AliasGroup

app = typer.Typer(cls=AliasGroup)


@app.command(RESTART_APP_CMD_ALIASES, help=RESTART_APP_CMD_HELP)
def restart_cluster_orchestrator_compose_service(
    compose_service: ClusterOrchestratorService,
) -> None:
    restart_docker_service(docker_compose_service=compose_service)


@app.command(REBUILD_APP_CMD_ALIASES, help=REBUILD_APP_CMD_HELP)
def rebuild_cluster_orchestrator_compose_service(
    compose_service: ClusterOrchestratorService,
    cache_less: Annotated[
        bool,
        typer.Option(help="Uses cache-less rebuild."),
    ] = False,
) -> None:
    rebuild_docker_compose_service(compose_service=compose_service, cache_less=cache_less)
