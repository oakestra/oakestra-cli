import csv
import os
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
        stop()
        clear_evaluation_csv()
    # https://peps.python.org/pep-3143/
    with daemon.DaemonContext():
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
                    "CPU Usage (%)",
                    "Memory Usage (%)",
                ]
            )
            while True:
                current_time_unix = time.time()
                current_time_human_readable = time.ctime(current_time_unix)
                writer.writerow(
                    [
                        current_time_unix,
                        current_time_human_readable,
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

    # Load the CSV file into a DataFrame
    df = pd.read_csv(EVALUATION_CSV)

    # Convert the timestamp column to datetime format
    df["Timestamp (Human Readable)"] = pd.to_datetime(df["Timestamp (Human Readable)"])

    # Set the timestamp column as the index
    df.set_index("Timestamp (Unix Epoch)", inplace=True)

    print("Columns:", df.columns.tolist())
    from icecream import ic

    # ic(df["Timestamp (Human Readable)"])
    # Create the time series plot
    plt.figure(figsize=(10, 6))  # Adjust the figure size as needed
    sns.lineplot(data=df[["Timestamp (Human Readable)", "CPU Usage (%)", "Memory Usage (%)"]])
    plt.title("Time Series of CPU and Memory Usage")
    print(1)
    plt.xlabel("Date")
    plt.ylabel("Usage (%)")
    plt.xticks(rotation=45)  # Rotate x-axis labels for better readability
    print(2)
    plt.show()
    print(3)


@app.command("clear-csv")
def clear_evaluation_csv() -> None:
    clear_file(EVALUATION_CSV)


@app.command("stop")
def stop() -> None:
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
