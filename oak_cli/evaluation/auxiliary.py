import os
import pathlib
import signal

SCRAPE_INTERVAL = 5  # In seconds

PID_FILE_PREFIX = pathlib.Path("/tmp")
EVALUATION_CSV_PREFIX = pathlib.Path("/tmp")


def to_mb(value: float) -> float:
    return value / (1024 * 1024)


def clear_file(file: pathlib.Path) -> None:
    # Open the file in write mode ('w'), which automatically truncates it
    with open(file, "w"):
        pass  # No need to write anything; just opening in 'w' mode clears the file


def kill_process(pid: int) -> None:
    # TODO rework
    try:
        # Attempt to send SIGTERM to the process
        os.kill(pid, signal.SIGTERM)
        print(f"Sent SIGTERM to process {pid}")
    except ProcessLookupError:
        # Handle case where pid does not exist
        print(f"No process found with PID {pid}")
