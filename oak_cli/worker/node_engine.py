from typing import Optional

import typer
from typing_extensions import Annotated

from oak_cli.utils.common import get_env_var, run_in_shell
from oak_cli.utils.logging import logger
from oak_cli.utils.typer_augmentations import AliasGroup
from oak_cli.worker.common import ProcessStatus, get_process_status, stop_process

app = typer.Typer(cls=AliasGroup)


NODE_ENGINE_NAME = "NodeEngine"
NODE_ENGINE_CMD_PREFIX = f"sudo {NODE_ENGINE_NAME}"


@app.command("start", help=f"Starts the {NODE_ENGINE_NAME}.")
def start_node_engine(
    use_ml_data_server_for_flops_addon_learner: Annotated[
        Optional[bool], typer.Option("--ml_data_server_for_flops_addon_learner")
    ] = False,
) -> None:
    if get_node_engine_status(print_status=False) == ProcessStatus.RUNNING:
        logger.info("The NodeEngine is already running.")
        return

    cmd = f"{NODE_ENGINE_CMD_PREFIX} -p 6000 -p 10100 -a {get_env_var(name='SYSTEM_MANAGER_URL')}"
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
