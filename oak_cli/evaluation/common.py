import pathlib

SCRAPE_INTERVAL = 5  # In seconds


def get_csv_file_path(csv_dir: pathlib.Path, evaluation_run_id: int = 1) -> pathlib.Path:
    return csv_dir / f"evaluation_run_{evaluation_run_id}.csv"
