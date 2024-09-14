from typing import Optional

import typer
from typing_extensions import Annotated

from oak_cli.utils.common import CaptureOutputType, run_in_shell
from oak_cli.utils.logging import logger
from oak_cli.utils.typer_augmentations import AliasGroup
from oak_cli.worker.common import ProcessStatus, get_process_status, stop_process

app = typer.Typer(cls=AliasGroup)


NET_MANAGER_NAME = "NetManager"
NET_MANAGER_CMD_PREFIX = f"sudo {NET_MANAGER_NAME}"


@app.command("start", help=f"Starts the {NET_MANAGER_NAME}.")
def start_net_manager(
    use_debug_mode: Annotated[Optional[bool], typer.Option("-D", help="Use debug mode")] = False,
    background: Annotated[bool, typer.Option("-b", help="Run in background")] = False,
) -> None:
    if get_net_manager_status(print_status=False) == ProcessStatus.RUNNING:
        logger.info("The NetManager is already running.")
        return

    cmd = f"{NET_MANAGER_CMD_PREFIX} -p 6000"
    if use_debug_mode:
        cmd += " -D"
    if background:
        cmd += " &"

    run_in_shell(
        shell_cmd=cmd,
        capture_output_type=(
            CaptureOutputType.HIDE_OUTPUT if background else CaptureOutputType.TO_STDOUT
        ),
        check=False,
        pure_shell=background,
    )
    if background:
        logger.info("Started the NetManager.")


@app.command("status", help=f"Show the status of the {NET_MANAGER_NAME}.")
def get_net_manager_status(print_status: bool = True) -> ProcessStatus:
    return get_process_status(
        process_cmd=NET_MANAGER_CMD_PREFIX,
        process_name=NET_MANAGER_NAME,
        print_status=print_status,
    )


@app.command("stop", help=f"stops the {NET_MANAGER_NAME}.")
def stop_net_manager() -> None:
    stop_process(process_cmd=NET_MANAGER_CMD_PREFIX, process_name=NET_MANAGER_NAME)


@app.command("restart", help=f"restarts the {NET_MANAGER_NAME}.")
def restart_net_manager() -> None:
    stop_net_manager()
    start_net_manager()
