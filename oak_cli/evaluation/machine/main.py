import csv
import os
import pathlib
import sys
import time

import ansible_runner
import daemon
import matplotlib.pyplot as plt
import pandas as pd
import psutil
import seaborn as sns
import typer

from oak_cli.ansible.python_utils import CLI_ANSIBLE_PATH, CliPlaybook
from oak_cli.evaluation.auxiliary import (
    EVALUATION_CSV_PREFIX,
    PID_FILE_PREFIX,
    SCRAPE_INTERVAL,
    clear_file,
    kill_process,
)
from oak_cli.utils.common import CaptureOutputType, run_in_shell
from oak_cli.utils.logging import logger

EVALUATION_CSV = EVALUATION_CSV_PREFIX / "machine_metrics.csv"
PIDFILE = PID_FILE_PREFIX / "oak_cli_evaluation_cpu"

app = typer.Typer()


@app.command("start")
def start() -> None:
    # https://peps.python.org/pep-3143/
    with daemon.DaemonContext():
        experiment_start_time = time.time()
        experiment_start_disk_space_used = psutil.disk_usage("/").used / (1024 * 1024)
        with open(PIDFILE, mode="w") as file:
            # NOTE: This needs to be called in the daemon context, otherwise the PID will be wrong!
            file.write(str(os.getpid()))
        with open(EVALUATION_CSV, mode="a", newline="") as file:
            writer = csv.writer(file)
            # Create the header row for CSV.
            writer.writerow(
                [
                    "Timestamp (Unix Epoch)",
                    "Timestamp (Human Readable)",
                    "Time since experiment start",
                    "Disk Space Utilization (%)",
                    "Disk Space change since start",
                    "CPU Usage (%)",
                    "Memory Usage (%)",
                ]
            )
            while True:
                current_time_unix = time.time()
                current_time_human_readable = time.ctime(current_time_unix)
                time_since_experiment_start = current_time_unix - experiment_start_time
                disk_stats = psutil.disk_usage("/")
                # Convert bytes to megabytes for easier reading
                current_used_mb = disk_stats.used / (1024 * 1024)
                diff_used_mb_since_start = experiment_start_disk_space_used - current_used_mb
                current_disk_utilization_percentage = disk_stats.percent

                writer.writerow(
                    [
                        current_time_unix,
                        current_time_human_readable,
                        time_since_experiment_start,
                        current_disk_utilization_percentage,
                        diff_used_mb_since_start,
                        psutil.cpu_percent(),
                        psutil.virtual_memory().percent,
                    ]
                )
                file.flush()
                time.sleep(SCRAPE_INTERVAL)


@app.command("show")
def show_results(live: bool = False, graph: bool = False) -> None:
    if not EVALUATION_CSV.exists():
        logger.warning(f"The file '{EVALUATION_CSV}' does not exist.")
        sys.exit(1)

    if not graph:
        run_in_shell(
            shell_cmd=f"tail -f {EVALUATION_CSV}" if live else f"cat {EVALUATION_CSV}",
            capture_output_type=CaptureOutputType.TO_STDOUT,
        )
        return

    # NOTE: Ideally this function would not only open the notebook (what it already does)
    # but also run all cells (to avoid the one manual click left).
    # So far I could not find a nice way of doing this.
    # TODO -> put into uval utils
    path = pathlib.Path(__file__).resolve().parent / "graph.ipynb"
    run_in_shell(shell_cmd=f"code {path}")


@app.command("clean")
def clean_up() -> None:
    """Cleans any remaining experiment artifacts to be ready for a new experiment.
    - Clears the contents of the PID and CSV file(s).
    - Kills any daemons.
    """
    clear_file(EVALUATION_CSV)
    stop()


@app.command("stop")
def stop() -> None:
    """Stops the experiment.
    - Kills its daemon
    - Clears its PID file contents
    """
    if not PIDFILE.exists():
        logger.warning(f"The file '{PIDFILE}' does not exist.")
        sys.exit(1)
    if PIDFILE.stat().st_size == 0:
        logger.warning(f"The file '{PIDFILE}' is empty.")
        sys.exit(1)

    with open(PIDFILE, "r") as file:
        pid = int(file.readline())
    kill_process(pid)
    clear_file(PIDFILE)


@app.command("test")
def test() -> None:
    # TODO: refactor this to call "run via ansible method", that will set the proper arguments
    # e.g. project_dir seems to be necessary to get the proper ansible context (ansible.cfg, etc.)
    ansible_runner.run(
        # private_data_dir=CLI_ANSIBLE_PATH, # <- wrong
        project_dir=str(CLI_ANSIBLE_PATH),
        playbook=CliPlaybook.EVALUATE_LOCALHOST.get_path(),
    )
