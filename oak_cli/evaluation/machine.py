import csv
import os
import sys
import time

import daemon
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
        logger.warning("Please first terminate the ongoing evaluation before starting a new one.")
        sys.exit(1)
    with daemon.DaemonContext():
        with open(PIDFILE, mode="w") as file:
            # NOTE: This needs to be called in the daemon context, otherwise the PID will be wrong!
            file.write(str(os.getpid()))
        with open(EVALUATION_CSV, mode="a", newline="") as file:
            writer = csv.writer(file)
            while True:
                current_time_unix = time.time()
                current_time_human_readable = time.ctime(current_time_unix)
                with open(EVALUATION_CSV, mode="a", newline="") as file:
                    writer = csv.writer(file)
                    writer.writerow([current_time_human_readable, current_time_unix])
                time.sleep(SCRAPE_INTERVAL)


@app.command("show-live")
def show_live_csv_results() -> None:
    if not EVALUATION_CSV.exists():
        logger.warning(f"The file '{EVALUATION_CSV}' does not exist.")
        sys.exit(1)
    run_in_shell(
        shell_cmd=f"tail -f {EVALUATION_CSV}",
        capture_output_type=CaptureOutputType.TO_STDOUT,
    )


@app.command("clear-csv")
def clear_evaluation_csv() -> None:
    clear_file(EVALUATION_CSV)


@app.command("stop")
def stop() -> None:
    with open(PIDFILE, "r") as file:
        pid = int(file.readline())
    kill_process(pid)
    clear_file(PIDFILE)
