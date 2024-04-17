import pathlib
import shlex
import subprocess
import sys

from oak_cli.commands.docker.common import check_docker_service_status
from oak_cli.commands.docker.enums import OakestraDockerComposeService, RootOrchestratorService
from oak_cli.utils.logging import logger

ROOT_ORCHESTRATOR_DOCKER_COMPOSE_FILE_PATH = pathlib.Path(
    "/home/alex/oakestra/root_orchestrator/docker-compose.yml"
)
CLUSTER_ORCHESTRATOR_DOCKER_COMPOSE_FILE_PATH = pathlib.Path(
    "/home/alex/oakestra/cluster_orchestrator/docker-compose.yml"
)


def rebuild_docker_service(docker_service: OakestraDockerComposeService) -> None:
    rebuild_flags = "-d --build --no-deps --force-recreate"
    if isinstance(docker_service, RootOrchestratorService):
        compose_path = ROOT_ORCHESTRATOR_DOCKER_COMPOSE_FILE_PATH
    else:
        compose_path = CLUSTER_ORCHESTRATOR_DOCKER_COMPOSE_FILE_PATH

    final_cmd = f"docker compose -f {compose_path} up {rebuild_flags} {docker_service}"

    result = subprocess.run(
        shlex.split(final_cmd),
        check=False,
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True,
    )
    if result.returncode != 0:
        logger.critical(f"Docker service '{docker_service}' rebuild failed due to: '{result}")
        sys.exit(1)

    check_docker_service_status(docker_service, "rebuild")
