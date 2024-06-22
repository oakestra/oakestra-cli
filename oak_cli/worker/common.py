import enum

from oak_cli.utils.common import run_in_shell
from oak_cli.utils.logging import logger


class ProcessStatus(enum.Enum):
    RUNNING = "Running 🟢"
    OFFLINE = "Offline ⚫"


def get_process_status(
    process_cmd: str,
    process_name: str = "",
    print_status: bool = False,
) -> ProcessStatus:
    cmd_res = run_in_shell(
        shell_cmd=f"ps -aux | grep '{process_cmd}'",
        pure_shell=True,
        text=True,
    )
    processes = [line for line in cmd_res.stdout.split("\n") if line != ""]
    message = ""
    if process_name:
        message = f"{process_name}: "
    # NOTE: The grep cmd and the python subprocess call count as 2 processes in the list.
    if len(processes) > 2:
        status = ProcessStatus.RUNNING
    else:
        status = ProcessStatus.OFFLINE

    if print_status:
        logger.info(message + status.value)

    return status


def stop_process(process_cmd: str, process_name: str) -> None:
    if get_process_status(process_cmd) == ProcessStatus.OFFLINE:
        logger.info(f"The {process_name} is already offline.")
        return

    cmd_res = run_in_shell(
        shell_cmd=f"ps -aux | grep '{process_cmd}' | awk '{{print $2}}'",
        pure_shell=True,
        text=True,
    )
    pids = [line for line in cmd_res.stdout.split("\n") if line != ""]
    # NOTE: The grep cmd and the python subprocess call count as 2 processes in the list.
    if len(pids) > 2:
        # NOTE: Killing the first PID in the list should stop the main process.
        # Thus, triggering a chain of events to remove all connected processes too.
        run_in_shell(shell_cmd=f"sudo kill {pids[0]}")
        logger.info(f"Stopped the {process_name}.")
