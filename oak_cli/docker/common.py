import json
import pathlib
import sys

from oak_cli.configuration.auxiliary import get_main_oak_repo_path
from oak_cli.docker.enums import OakestraDockerComposeService, RootOrchestratorService
from oak_cli.utils.common import run_in_shell
from oak_cli.utils.logging import logger
from oak_cli.utils.styling import create_spinner


def get_root_orchestrator_docker_compose_file_path() -> pathlib.Path:
    return get_main_oak_repo_path() / "root_orchestrator" / "docker-compose.yml"


def get_cluster_orchestrator_docker_compose_file_path() -> pathlib.Path:
    return get_main_oak_repo_path() / "cluster_orchestrator" / "docker-compose.yml"


def check_docker_service_status(
    docker_service: OakestraDockerComposeService,
    docker_operation: str,
) -> None:
    result = run_in_shell(
        shell_cmd='docker inspect -f "{{ json .State }}" ' + str(docker_service), text=True
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
    with create_spinner(message=f"Restarting '{docker_compose_service}'"):
        run_in_shell(shell_cmd=f"docker restart {docker_compose_service}", text=True)
    check_docker_service_status(docker_compose_service, "restarted")


def rebuild_docker_compose_service(
    compose_service: OakestraDockerComposeService,
    cache_less: bool = False,
) -> None:
    def handle_shell_cmd(cmd: str) -> None:
        result = run_in_shell(shell_cmd=cmd, text=True, check=False)
        if result.returncode != 0:
            logger.critical(
                f"Compose service '{compose_service}' operation '{cmd}' failed due to: '{result}"
            )
            sys.exit(1)

    if isinstance(compose_service, RootOrchestratorService):
        compose_path = get_root_orchestrator_docker_compose_file_path()
    else:
        compose_path = get_cluster_orchestrator_docker_compose_file_path()

    spinner_msg = f"Rebuilding '{compose_service}'"
    if cache_less:
        spinner_msg += " without cache"
    with create_spinner(message=spinner_msg):
        if cache_less:
            handle_shell_cmd(f"docker compose -f {compose_path} build --no-cache {compose_service}")
        re_up_flags = "--detach --build --no-deps --force-recreate"
        handle_shell_cmd(f"docker compose -f {compose_path} up {re_up_flags} {compose_service}")

    check_docker_service_status(compose_service, "rebuild")
