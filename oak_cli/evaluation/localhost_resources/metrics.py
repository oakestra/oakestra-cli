import csv
import os
import time

import daemon
import psutil

from oak_cli.evaluation.auxiliary import SCRAPE_INTERVAL, to_mb
from oak_cli.evaluation.localhost_resources.common import EVALUATION_CSV, PIDFILE, ExperimentCSVKeys


def start_metrics_collector_daemon():
    # https://peps.python.org/pep-3143/
    with daemon.DaemonContext():
        collect_metrics()


def collect_metrics():
    experiment_start_time = time.time()
    # Disk
    experiment_start_disk_space_used_mb = to_mb(psutil.disk_usage("/").used)
    last_disk_space_used_mb = experiment_start_disk_space_used_mb
    # Network
    experiment_start_bytes_received = psutil.net_io_counters().bytes_recv
    experiment_start_bytes_send = psutil.net_io_counters().bytes_sent
    last_bytes_received = experiment_start_bytes_received
    last_bytes_send = experiment_start_bytes_send

    with open(PIDFILE, mode="w") as file:
        # NOTE: This needs to be called in the daemon context, otherwise the PID will be wrong.
        file.write(str(os.getpid()))
    with open(EVALUATION_CSV, mode="a", newline="") as file:
        writer = csv.writer(file)
        # Write CSV Header
        writer.writerow([key.value for key in ExperimentCSVKeys])
        while True:
            current_time_unix = time.time()
            time_since_experiment_start = current_time_unix - experiment_start_time
            # Disk
            disk_stats = psutil.disk_usage("/")
            current_used_mb = to_mb(disk_stats.used)
            diff_used_disk_mb_since_start = current_used_mb - experiment_start_disk_space_used_mb
            next_disk_space_used = current_used_mb - last_disk_space_used_mb
            last_disk_space_used_mb = current_used_mb
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
                    # Time
                    current_time_unix,
                    time_since_experiment_start,
                    # Disk
                    diff_used_disk_mb_since_start,
                    disk_stats.used,
                    next_disk_space_used,
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
