import csv
import os
import pathlib
import sys
import time

import ansible_runner
import daemon
import psutil
import typer

from oak_cli.ansible.python_utils import CLI_ANSIBLE_PATH, CliPlaybook
from oak_cli.evaluation.auxiliary import (
    EVALUATION_CSV_PREFIX,
    PID_FILE_PREFIX,
    SCRAPE_INTERVAL,
    STAGE_FILE_PREFIX,
    clear_file,
    kill_process,
)
from oak_cli.utils.common import CaptureOutputType, run_in_shell
from oak_cli.utils.logging import logger

EVALUATION_CSV = EVALUATION_CSV_PREFIX / "machine_metrics.csv"
PIDFILE = PID_FILE_PREFIX / "oak_cli_evaluation_cpu"
STAGE_FILE = STAGE_FILE_PREFIX / "flops_stage"

app = typer.Typer()


@app.command("start")
def start() -> None:
    if not STAGE_FILE.exists():
        with open(STAGE_FILE, "w") as file:
            file.write("experiment start")

    # https://peps.python.org/pep-3143/
    with daemon.DaemonContext():
        experiment_start_time = time.time()
        # Disk
        experiment_start_disk_space_used_mb = psutil.disk_usage("/").used / (1024 * 1024)
        last_disk_space_used_mb = experiment_start_disk_space_used_mb
        # Network
        experiment_start_bytes_received = psutil.net_io_counters().bytes_recv
        experiment_start_bytes_send = psutil.net_io_counters().bytes_sent
        last_bytes_received = experiment_start_bytes_received
        last_bytes_send = experiment_start_bytes_send

        with open(PIDFILE, mode="w") as file:
            # NOTE: This needs to be called in the daemon context, otherwise the PID will be wrong!
            file.write(str(os.getpid()))
        with open(EVALUATION_CSV, mode="a", newline="") as file:
            writer = csv.writer(file)
            # Create the header row for CSV.
            writer.writerow(
                [
                    "Stage",
                    # Time
                    "Timestamp (Unix Epoch)",
                    "Time since experiment start",
                    # Disk
                    "Disk Space Utilization (%)",
                    "Disk Space change since start",
                    "Disk Space used",
                    "Next Disk diff",
                    # CPU & Memory
                    "CPU Usage (%)",
                    "Memory Usage (%)",
                    # Network
                    "Net Received Delta compared to start",
                    "Net Set Delta compared to start",
                    "Net Received Delta compared to last",
                    "Net Set Delta compared to last",
                ]
            )
            while True:
                current_time_unix = time.time()
                time_since_experiment_start = current_time_unix - experiment_start_time
                # Disk
                disk_stats = psutil.disk_usage("/")
                current_used_mb = disk_stats.used / (1024 * 1024)
                diff_used_mb_since_start = current_used_mb - experiment_start_disk_space_used_mb
                current_disk_utilization_percentage = disk_stats.percent
                next_disk_space_used = current_used_mb - last_disk_space_used_mb
                last_disk_space_used_mb = current_used_mb
                # Network
                current_bytes_received = psutil.net_io_counters().bytes_recv
                current_bytes_send = psutil.net_io_counters().bytes_sent

                compared_to_start_received = (
                    current_bytes_received - experiment_start_bytes_received
                )
                compared_to_start_send = current_bytes_send - experiment_start_bytes_send

                new_received = current_bytes_received - last_bytes_received
                new_send = current_bytes_send - last_bytes_send

                last_bytes_received = current_bytes_received
                last_bytes_send = current_bytes_send

                with open(STAGE_FILE, "r") as stage_file:
                    stage = stage_file.readline().replace("\n", "") or "experiment start"

                writer.writerow(
                    [
                        stage,
                        # Time
                        current_time_unix,
                        time_since_experiment_start,
                        # Disk
                        current_disk_utilization_percentage,
                        diff_used_mb_since_start,
                        disk_stats.used,
                        next_disk_space_used,
                        # CPU & Memory
                        psutil.cpu_percent(),
                        psutil.virtual_memory().percent,
                        # Network
                        compared_to_start_received / 1024 / 1024,
                        compared_to_start_send / 1024 / 1024,
                        new_received / 1024 / 1024,
                        new_send / 1024 / 1024,
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
    clear_file(STAGE_FILE)
    stop()


@app.command("stop")
def stop() -> None:
    """Stops the experiment.
    - Kills its daemon
    - Clears its PID file contents
    """
    if not PIDFILE.exists():
        logger.info(f"The file '{PIDFILE}' does not exist.")
        return
    if PIDFILE.stat().st_size == 0:
        logger.info(f"The file '{PIDFILE}' is empty.")
        return

    with open(PIDFILE, "r") as file:
        pid = int(file.readline())
    kill_process(pid)
    clear_file(PIDFILE)
    clear_file(STAGE_FILE)


@app.command("test")
def test() -> None:
    # TODO: refactor this to call "run via ansible method", that will set the proper arguments
    # e.g. project_dir seems to be necessary to get the proper ansible context (ansible.cfg, etc.)
    ansible_runner.run(
        # private_data_dir=CLI_ANSIBLE_PATH, # <- wrong
        project_dir=str(CLI_ANSIBLE_PATH),
        playbook=CliPlaybook.EVALUATE_LOCALHOST.get_path(),
    )
