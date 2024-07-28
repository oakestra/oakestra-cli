from typing import List

import pandas

from oak_cli.evaluation.localhost_resources.common import ExperimentCSVKeys

CPU_AND_MEMORY_KEYS = [ExperimentCSVKeys.CPU_USAGE.value, ExperimentCSVKeys.MEMORY_USAGE.value]


def get_experiment_duration_label(use_minutes: bool = True) -> str:
    return "Experiment Duration " + "(minutes)" if use_minutes else "(seconds)"


def apply_rolling_window(
    df: pandas.DataFrame,
    keys: List[ExperimentCSVKeys],
    window_size: int = 10,
    use_mean: bool = True,
) -> None:
    tmp = df[keys].rolling(window=window_size)
    df[keys] = tmp.mean() if use_mean else tmp.median()
