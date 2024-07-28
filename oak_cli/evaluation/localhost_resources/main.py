import sys

import ansible_runner
import typer

from oak_cli.ansible.python_utils import CLI_ANSIBLE_PATH, CliPlaybook
from oak_cli.evaluation.auxiliary import clear_file, kill_process
from oak_cli.evaluation.localhost_resources.common import EVALUATION_CSV, PIDFILE
from oak_cli.evaluation.localhost_resources.metrics import start_metrics_collector_daemon
from oak_cli.utils.common import CaptureOutputType, run_in_shell
from oak_cli.utils.logging import logger

app = typer.Typer()


@app.command("start-manual-experiment")
def start_manual_experiment() -> None:
    start_metrics_collector_daemon()


@app.command("start-automatic-experiment")
def start_automatic_experiment() -> None:
    # NOTE: This playbook requires ansible-galaxy dependencies to be installed on the machine.
    # Installing it via a dedicated playbook does not work due to ansible-access right issues.
    run_in_shell(shell_cmd="ansible-galaxy collection install community.docker")
    ansible_runner.run(
        project_dir=str(CLI_ANSIBLE_PATH),
        playbook=CliPlaybook.EVALUATE_LOCALHOST.get_path(),
    )


@app.command("show-csv")
def show_csv(live: bool = False) -> None:
    if not EVALUATION_CSV.exists():
        logger.warning(f"The file '{EVALUATION_CSV}' does not exist.")
        sys.exit(1)

    run_in_shell(
        shell_cmd=f"tail -f {EVALUATION_CSV}" if live else f"cat {EVALUATION_CSV}",
        capture_output_type=CaptureOutputType.TO_STDOUT,
    )


@app.command("clean")
def clean_up() -> None:
    """Cleans any remaining experiment artifacts to be ready for a new experiment.
    - Clears the contents of the PID and CSV file(s).
    - Kills any daemons.
    """
    clear_file(EVALUATION_CSV)
    stop_experiment()


@app.command("stop-experiment")
def stop_experiment() -> None:
    """Stops the experiment.
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
