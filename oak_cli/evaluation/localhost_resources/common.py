import enum
import pathlib

EVALUATION_CSV = pathlib.Path("/tmp/machine_metrics.csv")
PIDFILE = pathlib.Path("/tmp/oak_cli_evaluation_cpu")


class ExperimentCSVKeys(enum.Enum):
    # Time
    UNIX_TIMESTAMP = "UNIX Timestamp"
    TIME_SINCE_START = "Time Since Experiment Start"
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
