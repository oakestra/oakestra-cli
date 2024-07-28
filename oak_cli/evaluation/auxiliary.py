import os
import pathlib
import shutil
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


def clear_dir(dir: pathlib.Path) -> None:
    if dir.exists():
        shutil.rmtree(dir)


def kill_process(pid: int) -> None:
    # TODO rework
    try:
        # Attempt to send SIGTERM to the process
        os.kill(pid, signal.SIGTERM)
        print(f"Sent SIGTERM to process {pid}")
    except ProcessLookupError:
        # Handle case where pid does not exist
        print(f"No process found with PID {pid}")


def get_csv_file_path(csv_dir: pathlib.Path, experiment_id: int = 1) -> pathlib.Path:
    return csv_dir / f"experiment_{experiment_id}.csv"


import seaborn as sns

sns.lineplot()
