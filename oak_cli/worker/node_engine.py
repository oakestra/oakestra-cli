import enum
import os
from typing import Optional

import typer
from typing_extensions import Annotated

from oak_cli.configuration.auxiliary import get_main_oak_repo_path
from oak_cli.configuration.common import get_config_value
from oak_cli.configuration.keys.enums import ConfigurableConfigKey
from oak_cli.configuration.local_machine_purpose import (
    LocalMachinePurpose,
    check_if_local_machine_has_required_purposes,
)
from oak_cli.utils.common import run_in_shell
from oak_cli.utils.logging import logger
from oak_cli.utils.typer_augmentations import AliasGroup
from oak_cli.worker.common import ProcessStatus, get_process_status, stop_process


class Architecture(enum.Enum):
    AMD64 = "amd64"
    ARM64 = "arm64"


NODE_ENGINE_NAME = "NodeEngine"
NODE_ENGINE_CMD_PREFIX = f"sudo {NODE_ENGINE_NAME}"


app = typer.Typer(cls=AliasGroup)


@app.command("start", help=f"Starts the {NODE_ENGINE_NAME}.")
def start_node_engine(
    use_ml_data_server_for_flops_addon_learner: Annotated[
        Optional[bool], typer.Option("--ml_data_server_for_flops_addon_learner")
    ] = False,
) -> None:
    if get_node_engine_status(print_status=False) == ProcessStatus.RUNNING:
        logger.info("The NodeEngine is already running.")
        return

    cmd = " ".join(
        (
            NODE_ENGINE_CMD_PREFIX,
            "-p 6000 -p 10100",
            "-a",
            get_config_value(ConfigurableConfigKey.CLUSTER_MANAGER_IP),
        )
    )
    if use_ml_data_server_for_flops_addon_learner:
        cmd += " -l"
    run_in_shell(shell_cmd=cmd, capture_output=False, check=False)


@app.command("status", help=f"Show the status of the {NODE_ENGINE_NAME}.")
def get_node_engine_status(print_status: bool = True) -> ProcessStatus:
    return get_process_status(
        process_cmd=NODE_ENGINE_CMD_PREFIX,
        process_name=NODE_ENGINE_NAME,
        print_status=print_status,
    )


@app.command("stop", help=f"stops the {NODE_ENGINE_NAME}.")
def stop_node_engine() -> None:
    stop_process(process_cmd=NODE_ENGINE_CMD_PREFIX, process_name=NODE_ENGINE_NAME)


if check_if_local_machine_has_required_purposes(
    required_purposes=[LocalMachinePurpose.DEVELOPMENT]
):
    # TODO: Figure out architecture automatically.
    @app.command(
        "rebuild",
        help=f"rebuilds (and restarts) the {NODE_ENGINE_NAME}.",
    )
    def rebuild_node_engine(
        # NOTE: Theoretically this is wrong but it only works like this - typer is WIP after all.
        architecture: Architecture = Architecture.AMD64.value,
        restart: bool = True,
    ) -> None:
        if restart:
            stop_node_engine()

        node_engine_build_path = get_main_oak_repo_path() / "go_node_engine" / "build"
        os.chdir(node_engine_build_path)
        run_in_shell(shell_cmd="bash build.sh")
        run_in_shell(shell_cmd=f"bash install.sh {architecture.value}")
        logger.info("Successfully rebuild the NodeEngine.")

        if restart:
            start_node_engine()
