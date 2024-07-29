import sys

import ansible_runner
import typer

from oak_cli.ansible.python_utils import CLI_ANSIBLE_PATH, CliPlaybook
from oak_cli.evaluation.common import get_csv_file_path
from oak_cli.evaluation.resources.common import CSV_DIR, PIDFILE
from oak_cli.utils.common import (
    CaptureOutputType,
    clear_dir,
    clear_file,
    kill_process,
    run_in_shell,
)
from oak_cli.utils.logging import logger

app = typer.Typer()


@app.command("start-automatic-evaluation-cycle")
def start_evaluation_cycle(number_of_evaluation_runs: int = 10) -> None:
    # NOTE: This playbook requires ansible-galaxy dependencies to be installed on the machine.
    # Installing it via a dedicated playbook does not work due to ansible-access right issues.
    run_in_shell(shell_cmd="ansible-galaxy collection install community.docker")
    ansible_runner.run(
        project_dir=str(CLI_ANSIBLE_PATH),
        playbook=CliPlaybook.EVALUATE_RESOURCES.get_path(),
        extravars={"number_of_evaluation_runs": number_of_evaluation_runs},
    )


@app.command("show-csv")
def show_csv(live: bool = False, evaluation_run_id: int = 1) -> None:
    csv_file = get_csv_file_path(csv_dir=CSV_DIR, evaluation_run_id=evaluation_run_id)
    if not csv_file.exists():
        logger.warning(f"The file '{csv_file}' does not exist.")
        sys.exit(1)

    run_in_shell(
        shell_cmd=f"tail -f {csv_file}" if live else f"cat {csv_file}",
        capture_output_type=CaptureOutputType.TO_STDOUT,
    )


@app.command("clean")
def clean_up() -> None:
    """Cleans any remaining artifacts to be ready for a fresh new evaluation-cycle.
    This function should not be called between evaluation-runs.
    - Clears the contents of the PID and CSV files.
    - Kills any daemons.
    """
    clear_dir(CSV_DIR)
    stop_evaluation_run()


@app.command("stop-evaluation-run")
def stop_evaluation_run() -> None:
    """Stops the current evaluation-run.
    - Kills its daemon
    - Clears its PID file contents
    """
    if not PIDFILE.exists():
        logger.debug(f"The file '{PIDFILE}' does not exist.")
        return
    if PIDFILE.stat().st_size == 0:
        logger.debug(f"The file '{PIDFILE}' is empty.")
        return

    with open(PIDFILE, "r") as file:
        pid = int(file.readline())
    kill_process(pid)
    clear_file(PIDFILE)
