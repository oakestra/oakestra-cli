import pathlib
import shlex
import subprocess
import sys

from oak_cli.commands.docker.common import check_docker_service_status
from oak_cli.commands.docker.enums import OakestraDockerComposeService, RootOrchestratorService
from oak_cli.utils.logging import logger

ROOT_ORCHESTRATOR_DOCKER_COMPOSE_FILE_PATH = pathlib.Path(
    "/home/alex/oakestra_main_repo/root_orchestrator/docker-compose.yml"
)
CLUSTER_ORCHESTRATOR_DOCKER_COMPOSE_FILE_PATH = pathlib.Path(
    "/home/alex/oakestra_main_repo/cluster_orchestrator/docker-compose.yml"
)


def rebuild_docker_service(
    docker_service: OakestraDockerComposeService, cache_less: bool = False
) -> None:

    def run_shell_cmd(cmd: str) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            shlex.split(cmd),
            check=False,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True,
        )
        if result.returncode != 0:
            logger.critical(
                f"Docker service '{docker_service}' operation '{cmd}' failed due to: '{result}"
            )
            sys.exit(1)

    if isinstance(docker_service, RootOrchestratorService):
        compose_path = ROOT_ORCHESTRATOR_DOCKER_COMPOSE_FILE_PATH
    else:
        compose_path = CLUSTER_ORCHESTRATOR_DOCKER_COMPOSE_FILE_PATH

    if cache_less:
        run_shell_cmd(f"docker compose -f {compose_path} build --no-cache {docker_service}")
    re_up_flags = "--detach --build --no-deps --force-recreate"
    run_shell_cmd(f"docker compose -f {compose_path} up {re_up_flags} {docker_service}")

    check_docker_service_status(docker_service, "rebuild")
