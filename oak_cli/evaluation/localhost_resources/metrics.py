import csv
import os
import time

import daemon
import psutil

from oak_cli.evaluation.auxiliary import SCRAPE_INTERVAL, get_csv_file_path, to_mb
from oak_cli.evaluation.localhost_resources.common import CSV_DIR, PIDFILE, ExperimentCSVKeys


def start_metrics_collector_daemon(experiment_id: int = 1) -> None:
    # https://peps.python.org/pep-3143/
    with daemon.DaemonContext():
        collect_metrics(experiment_id)


def collect_metrics(experiment_id: int = 1) -> None:
    time__experiment_start__s = time.time()
    # Disk
    disk_space_used__experiment_start__mb = to_mb(psutil.disk_usage("/").used)
    disk_space_used__last_measurement__mb = disk_space_used__experiment_start__mb
    # Network
    experiment_start_bytes_received = psutil.net_io_counters().bytes_recv
    experiment_start_bytes_send = psutil.net_io_counters().bytes_sent
    last_bytes_received = experiment_start_bytes_received
    last_bytes_send = experiment_start_bytes_send

    with open(PIDFILE, mode="w") as file:
        # NOTE: This needs to be called in the daemon context, otherwise the PID will be wrong.
        file.write(str(os.getpid()))

    if not CSV_DIR.exists():
        CSV_DIR.mkdir(parents=True)

    csv_file = get_csv_file_path(csv_dir=CSV_DIR, experiment_id=experiment_id)

    if not csv_file.exists():
        csv_file.touch()

    with open(
        csv_file,
        mode="a",
        newline="",
    ) as file:
        writer = csv.writer(file)
        # Write CSV Header
        writer.writerow([key.value for key in ExperimentCSVKeys])
        while True:
            time__current_unix__s = time.time()
            time__since_experiment_start__s = time__current_unix__s - time__experiment_start__s
            # Disk
            disk_stats = psutil.disk_usage("/")
            disk_space_used__current__mb = to_mb(disk_stats.used)
            disk_space_used__diff_since_start__mb = (
                disk_space_used__current__mb - disk_space_used__experiment_start__mb
            )
            disk_space_used__diff_since_last_measurement__mb = (
                disk_space_used__current__mb - disk_space_used__last_measurement__mb
            )
            disk_space_used__last_measurement__mb = disk_space_used__current__mb
            # Network
            current_bytes_received = psutil.net_io_counters().bytes_recv
            current_bytes_send = psutil.net_io_counters().bytes_sent

            compared_to_start_received = current_bytes_received - experiment_start_bytes_received
            compared_to_start_send = current_bytes_send - experiment_start_bytes_send

            new_received = current_bytes_received - last_bytes_received
            new_send = current_bytes_send - last_bytes_send

            last_bytes_received = current_bytes_received
            last_bytes_send = current_bytes_send

            writer.writerow(
                [
                    experiment_id,
                    # Time
                    time__current_unix__s,
                    time__since_experiment_start__s,
                    # Disk
                    disk_space_used__diff_since_start__mb,
                    disk_space_used__diff_since_last_measurement__mb,
                    # CPU & Memory
                    psutil.cpu_percent(),
                    psutil.virtual_memory().percent,
                    # Network
                    to_mb(compared_to_start_received),
                    to_mb(compared_to_start_send),
                    to_mb(new_received),
                    to_mb(new_send),
                ]
            )
            file.flush()
            time.sleep(SCRAPE_INTERVAL)
