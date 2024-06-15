import json
import pathlib
import shlex
import subprocess
import sys

from oak_cli.docker.enums import OakestraDockerComposeService, RootOrchestratorService
from oak_cli.utils.logging import logger

ROOT_ORCHESTRATOR_DOCKER_COMPOSE_FILE_PATH = pathlib.Path(
    "/home/alex/oakestra_main_repo/root_orchestrator/docker-compose.yml"
)
CLUSTER_ORCHESTRATOR_DOCKER_COMPOSE_FILE_PATH = pathlib.Path(
    "/home/alex/oakestra_main_repo/cluster_orchestrator/docker-compose.yml"
)


def check_docker_service_status(
    docker_service: OakestraDockerComposeService,
    docker_operation: str,
) -> None:
    inspect_cmd = 'docker inspect -f "{{ json .State }}" ' + str(docker_service)
    result = subprocess.run(
        shlex.split(inspect_cmd),
        check=True,
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True,
    )
    result_output = json.loads(result.stdout)
    service_status = result_output["Status"]
    if service_status == "running":
        logger.info(
            f"'{docker_service}' successfully '{docker_operation}' - status: '{service_status}'"
        )
    else:
        logger.error(
            f"'{docker_service}' failed to '{docker_operation}' - status: '{service_status}'"
        )


def restart_docker_service(docker_compose_service: OakestraDockerComposeService) -> None:
    docker_cmd = f"docker restart {docker_compose_service}"
    subprocess.run(
        shlex.split(docker_cmd),
        check=True,
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True,
    )
    check_docker_service_status(docker_compose_service, "restarted")


def rebuild_docker_compose_service(
    compose_service: OakestraDockerComposeService,
    cache_less: bool = False,
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
                f"Compose service '{compose_service}' operation '{cmd}' failed due to: '{result}"
            )
            sys.exit(1)

    if isinstance(compose_service, RootOrchestratorService):
        compose_path = ROOT_ORCHESTRATOR_DOCKER_COMPOSE_FILE_PATH
    else:
        compose_path = CLUSTER_ORCHESTRATOR_DOCKER_COMPOSE_FILE_PATH

    if cache_less:
        run_shell_cmd(f"docker compose -f {compose_path} build --no-cache {compose_service}")
    re_up_flags = "--detach --build --no-deps --force-recreate"
    run_shell_cmd(f"docker compose -f {compose_path} up {re_up_flags} {compose_service}")

    check_docker_service_status(compose_service, "rebuild")
