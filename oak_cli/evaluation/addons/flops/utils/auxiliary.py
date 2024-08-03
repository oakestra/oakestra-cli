import pandas as pd

from oak_cli.evaluation.addons.flops.utils.keys import RUN_ID_KEY, TIME_START_KEY
from oak_cli.evaluation.addons.flops.utils.stages.auxiliary import (
    get_median_stage_durations,
    get_stage_durations_df,
)
from oak_cli.evaluation.graph_utils import ROUNDING_PRECISION


def normalize_df_time_ranges(data: pd.DataFrame) -> pd.DataFrame:
    stage_durations_df = get_stage_durations_df(data)
    median_stage_durations = get_median_stage_durations(stage_durations_df)
    median_runtime__minutes = median_stage_durations.sum()

    _data = data.copy()
    _data.reset_index(inplace=True)

    max_times = _data.groupby(RUN_ID_KEY)[TIME_START_KEY].max()

    for run_id in max_times.index:
        _data.loc[_data[RUN_ID_KEY] == run_id, TIME_START_KEY] = round(
            (_data[_data[RUN_ID_KEY] == run_id][TIME_START_KEY] / max_times[run_id])
            * median_runtime__minutes,
            ROUNDING_PRECISION,
        )

    _data.set_index(TIME_START_KEY, inplace=True)
    return _data
