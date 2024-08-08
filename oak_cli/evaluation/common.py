import csv
import os
import pathlib
import time

import daemon

from oak_cli.evaluation.addons.flops.main import (
    FLOpsMetricManagerMonolith,
    FLOpsMetricManagerMultiCluster,
    handle_flops_files_at_evaluation_run_start,
)
from oak_cli.evaluation.resources.main import ResourcesMetricManager
from oak_cli.evaluation.types import EvaluationScenario, MetricsManager

SCRAPE_INTERVAL = 5  # In seconds


def get_metrics_manager_for_scenario(scenario: EvaluationScenario) -> MetricsManager:
    match scenario:
        case EvaluationScenario.RESOURCES:
            return ResourcesMetricManager()
        case EvaluationScenario.FLOPS_MONOLITH:
            return FLOpsMetricManagerMonolith()
        case EvaluationScenario.FLOPS_MULTI_CLUSTER:
            return FLOpsMetricManagerMultiCluster()


def get_pid_file_for_scenario(scenario: EvaluationScenario) -> pathlib.Path:
    match scenario:
        case EvaluationScenario.RESOURCES:
            pid_file = "/tmp/resources_evaluation_pid_file"
        case EvaluationScenario.FLOPS_MONOLITH:
            pid_file = "/tmp/flops_evaluation_pid_file"
        case EvaluationScenario.FLOPS_MULTI_CLUSTER:
            pid_file = "/tmp/flops_evaluation_pid_file"
    return pathlib.Path(pid_file)


def get_csv_dir_for_scenario(scenario: EvaluationScenario) -> pathlib.Path:
    match scenario:
        case EvaluationScenario.RESOURCES:
            pid_file = "/tmp/resources_evaluation_runs/"
        case EvaluationScenario.FLOPS_MONOLITH:
            pid_file = "/tmp/flops_evaluation_runs/"
        case EvaluationScenario.FLOPS_MULTI_CLUSTER:
            pid_file = "/tmp/flops_evaluation_runs/"
    return pathlib.Path(pid_file)


def get_csv_file_path(csv_dir: pathlib.Path, evaluation_run_id: int = 1) -> pathlib.Path:
    return csv_dir / f"evaluation_run_{evaluation_run_id}.csv"


def start_evaluation_process(
    scenario: EvaluationScenario,
    evaluation_run_id: int,
) -> None:
    if scenario in [EvaluationScenario.FLOPS_MONOLITH, EvaluationScenario.FLOPS_MULTI_CLUSTER]:
        handle_flops_files_at_evaluation_run_start()

    # https://peps.python.org/pep-3143/
    with daemon.DaemonContext():
        metrics_manager = get_metrics_manager_for_scenario(scenario)
        pid_file = get_pid_file_for_scenario(scenario)
        csv_dir = get_csv_dir_for_scenario(scenario)

        with open(pid_file, mode="w") as file:
            file.write(str(os.getpid()))

        if not csv_dir.exists():
            csv_dir.mkdir(parents=True)

        csv_file = get_csv_file_path(csv_dir=csv_dir, evaluation_run_id=evaluation_run_id)

        if not csv_file.exists():
            csv_file.touch()

        with open(
            csv_file,
            mode="a",
            newline="",
        ) as file:
            writer = csv.writer(file)
            writer.writerow(metrics_manager.create_csv_header())
            while True:
                writer.writerow([evaluation_run_id] + metrics_manager.create_csv_line_entries())
                file.flush()
                time.sleep(SCRAPE_INTERVAL)
