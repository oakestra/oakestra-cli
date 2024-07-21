import os
import pathlib
import signal

SCRAPE_INTERVAL = 1  # In seconds

PID_FILE_PREFIX = pathlib.Path("/tmp")
EVALUATION_CSV_PREFIX = pathlib.Path("/tmp")


def clear_file(file: pathlib.Path) -> None:
    # Open the file in write mode ('w'), which automatically truncates it
    with open(file, "w"):
        pass  # No need to write anything; just opening in 'w' mode clears the file


def kill_process(pid: int) -> None:
    os.kill(pid, signal.SIGTERM)
