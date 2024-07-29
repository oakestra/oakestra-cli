import enum
import pathlib

RESOURCES_CSV_DIR = pathlib.Path("/tmp/resources_evaluation_runs/")
RESOURCES_PIDFILE = pathlib.Path("/tmp/resources_evaluation_pid_file")


class ResourcesCSVKeys(enum.Enum):
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
