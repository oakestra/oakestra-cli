import csv
import os
import pathlib
import sys
import time

import daemon
import matplotlib.pyplot as plt
import pandas as pd
import psutil
import seaborn as sns
import typer

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
    if PIDFILE.exists() and PIDFILE.stat().st_size > 0:
        logger.warning("Previous evaluation will be terminated.")
        clean_up()
    # https://peps.python.org/pep-3143/
    with daemon.DaemonContext():
        experiment_start_time = time.time()
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
                    "CPU Usage (%)",
                    "Memory Usage (%)",
                ]
            )
            while True:
                current_time_unix = time.time()
                current_time_human_readable = time.ctime(current_time_unix)
                time_since_experiment_start = current_time_unix - experiment_start_time
                writer.writerow(
                    [
                        current_time_unix,
                        current_time_human_readable,
                        time_since_experiment_start,
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
