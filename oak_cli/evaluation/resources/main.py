import time
from typing import Any, List

import psutil

from oak_cli.evaluation.types import CSVKeys, EvaluationScenario, MetricsManager
from oak_cli.utils.common import to_mb


class ResourcesCSVKeys(CSVKeys):
    EVALUATION_RUN_ID = "Evaluation-Run ID"
    # Time
    UNIX_TIMESTAMP = "UNIX Timestamp"
    TIME_SINCE_START = "Time Since Evaluation-Run Start"
    # Disk
    DISK_SPACE_CHANGE_SINCE_START = "Disk Space Change Since Start"
    DISK_SPACE_CHANGE_SINCE_LAST_MEASUREMENT = "Disk Space Change Since Last Measurement"
    # CPU & Memory
    CPU_USAGE = "CPU Usage"
    MEMORY_USAGE = "Memory Usage"
    # Network
    NETWORK_RECEIVED_SINCE_START = "Network Received Since Start"
    NETWORK_SENT_SINCE_START = "Network Sent Since Start"
    NETWORK_RECEIVED_COMPARED_TO_LAST_MEASUREMENT = "Network Received Compared To Last Measurement"
    NETWORK_SENT_COMPARED_TO_LAST_MEASUREMENT = "Network Sent Compared To Last Measurement"


class ResourcesMetricManager(MetricsManager):
    scenario = EvaluationScenario.RESOURCES

    time__evaluation_run_start__s: float = time.time()
    # Disk
    disk_space_used__evaluation_run_start__mb: float = to_mb(psutil.disk_usage("/").used)
    disk_space_used__last_measurement__mb: float = disk_space_used__evaluation_run_start__mb
    # Network
    # https://www.educative.io/answers/what-is-the-psutilnetiocounters-method
    evaluation_run_start_bytes_received: int = psutil.net_io_counters(nowrap=True).bytes_recv
    evaluation_run_start_bytes_send: int = psutil.net_io_counters(nowrap=True).bytes_sent
    last_bytes_received: int = evaluation_run_start_bytes_received
    last_bytes_send: int = evaluation_run_start_bytes_send

    def create_csv_header(self) -> List[str]:
        return [key.value for key in ResourcesCSVKeys]

    def create_csv_line_entries(self) -> List[Any]:
        time__current_unix__s = time.time()
        time__since_evaluation_run_start__s = (
            time__current_unix__s - self.time__evaluation_run_start__s
        )
        # Disk
        disk_stats = psutil.disk_usage("/")
        disk_space_used__current__mb = to_mb(disk_stats.used)
        disk_space_used__diff_since_start__mb = (
            disk_space_used__current__mb - self.disk_space_used__evaluation_run_start__mb
        )
        disk_space_used__diff_since_last_measurement__mb = (
            disk_space_used__current__mb - self.disk_space_used__last_measurement__mb
        )
        self.disk_space_used__last_measurement__mb = disk_space_used__current__mb
        # Network
        current_bytes_received = psutil.net_io_counters(nowrap=True).bytes_recv
        current_bytes_send = psutil.net_io_counters(nowrap=True).bytes_sent

        compared_to_start_received = (
            current_bytes_received - self.evaluation_run_start_bytes_received
        )
        compared_to_start_send = current_bytes_send - self.evaluation_run_start_bytes_send

        new_received = current_bytes_received - self.last_bytes_received
        new_send = current_bytes_send - self.last_bytes_send

        self.last_bytes_received = current_bytes_received
        self.last_bytes_send = current_bytes_send

        return [
            # Time
            time__current_unix__s,
            time__since_evaluation_run_start__s,
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
