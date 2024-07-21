import csv
import os
import signal
import subprocess
import tempfile
import time

import daemon
import typer

file_path = "/tmp/alex_timestamps.csv"

app = typer.Typer()
from icecream import ic

pidfile = "/tmp/oak_cli_evaluation_cpu"


@app.command("start-cpu", help="Evaluate CPU usage")
def start_evaluate_cpu() -> None:
    print("hi")

    if os.path.exists(pidfile) and os.path.getsize(pidfile) > 0:
        print("File is not empty")
        exit(1)
    else:
        print("File is empty")

    with daemon.DaemonContext():
        with open(pidfile, mode="w") as file:
            # NOTE: This needs to be called in the deamon context, otherwise the PID will be wrong!
            file.write(str(os.getpid()))

        with open(file_path, mode="a", newline="") as file:
            writer = csv.writer(file)
            while True:
                current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
                with open(file_path, mode="a", newline="") as file:
                    writer = csv.writer(file)
                    writer.writerow([current_time])

                time.sleep(1)


@app.command("stop-cpu", help="Evaluate CPU usage")
def stop_evaluate_cpu() -> None:
    print("chao")
    with open(pidfile, "r") as file:
        pid = int(file.readline())

    print(pid)
    signal_number = signal.SIGTERM

    try:
        os.kill(pid, signal_number)
        print(f"Sent {signal_number} to process {pid}")
    except PermissionError:
        print(f"Permission denied to kill process {pid}")
    except OSError as e:
        print(f"Failed to kill process {pid}: {e}")

    # Open the file in write mode ('w'), which automatically truncates it
    with open(pidfile, "w") as file:
        pass  # No need to write anything; just opening in 'w' mode clears the file
