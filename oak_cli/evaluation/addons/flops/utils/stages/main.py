import pandas as pd

from oak_cli.evaluation.addons.flops.main import EvaluationRunFLOpsProjectStage
from oak_cli.evaluation.addons.flops.utils.keys import RUN_ID_KEY, STAGE_KEY, TIME_START_KEY
from oak_cli.evaluation.graph_utils import ROUNDING_PRECISION

# Auxiliary numerical stage ID (instead of the string) for future numerical manipulations.
STAGE_ID_KEY = "STAGE ID"
STAGE_DURATIONS_KEY = "Stage Durations"


def _get_stage_durations_series(data: pd.DataFrame) -> pd.Series:
    _data = data.copy()
    _data.reset_index(inplace=True)
    _data[[TIME_START_KEY]] = round(_data[[TIME_START_KEY]], ROUNDING_PRECISION)
    grouped_by_stage_id_and_run_id_for_time_start = _data.groupby([STAGE_KEY, RUN_ID_KEY])[
        TIME_START_KEY
    ]
    stage_start_times = grouped_by_stage_id_and_run_id_for_time_start.min()
    stage_end_times = grouped_by_stage_id_and_run_id_for_time_start.max()
    stage_durations = stage_end_times - stage_start_times
    return stage_durations


def get_stage_durations_df(data: pd.DataFrame) -> pd.DataFrame:
    stage_durations = _get_stage_durations_series(data)
    stage_durations_df = pd.DataFrame(
        {
            STAGE_KEY: stage_durations.index.get_level_values(STAGE_KEY),
            RUN_ID_KEY: stage_durations.index.get_level_values(RUN_ID_KEY),
            STAGE_DURATIONS_KEY: stage_durations.values,
        }
    )
    stage_durations_df[STAGE_ID_KEY] = stage_durations_df[STAGE_KEY].apply(
        lambda stage_name: EvaluationRunFLOpsProjectStage(stage_name).get_index()
    )
    stage_durations_df.sort_values(by=STAGE_ID_KEY, inplace=True)

    # Remove all stages that were so fast that they took 0 seconds to complete.
    # NOTE: Might be an unnecessary stage in the first place.
    stage_durations_df = stage_durations_df[stage_durations_df[STAGE_DURATIONS_KEY] > 0]

    return stage_durations_df.copy().sort_values(by=STAGE_ID_KEY)


def get_median_stage_durations(stage_durations_df: pd.DataFrame) -> pd.Series:
    return stage_durations_df.groupby([STAGE_KEY])[STAGE_DURATIONS_KEY].median()
