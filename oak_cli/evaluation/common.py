import pathlib

import daemon

from oak_cli.evaluation.resources.metrics import collect_metrics

SCRAPE_INTERVAL = 5  # In seconds


def get_csv_file_path(csv_dir: pathlib.Path, evaluation_run_id: int = 1) -> pathlib.Path:
    return csv_dir / f"evaluation_run_{evaluation_run_id}.csv"


def start_evaluation_run_daemon(evaluation_run_id: int = 1) -> None:
    # https://peps.python.org/pep-3143/
    with daemon.DaemonContext():
        collect_metrics(evaluation_run_id)
