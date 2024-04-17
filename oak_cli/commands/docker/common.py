import json
import shlex
import subprocess

from oak_cli.commands.docker.enums import OakestraDockerComposeService
from oak_cli.utils.logging import logger


def check_docker_service_status(
    docker_service: OakestraDockerComposeService, docker_operation: str
):
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
