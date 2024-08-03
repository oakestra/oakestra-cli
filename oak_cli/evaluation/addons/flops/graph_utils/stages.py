from typing import List

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.patches import Patch
from pydantic import BaseModel

from oak_cli.evaluation.addons.flops.graph_utils.keys import RUN_ID_KEY, STAGE_KEY, TIME_START_KEY
from oak_cli.evaluation.addons.flops.main import (
    EvaluationRunFLOpsProjectStage,
    FLOpsExclusiveCSVKeys,
)
from oak_cli.evaluation.graph_utils import ROUNDING_PRECISION

# Auxiliary numerical stage ID (instead of the string) for future numerical manipulations.
STAGE_ID_KEY = "STAGE ID"
STAGE_DURATIONS_KEY = "Stage Durations"


class _Stage_Info(BaseModel):
    stage: EvaluationRunFLOpsProjectStage
    start: float = 0
    end: float = 0


def get_stage_durations_series(data: pd.DataFrame) -> pd.Series:
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
    stage_durations = get_stage_durations_series(data)
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


def _populate_stages_info(
    data: pd.DataFrame,
) -> List[_Stage_Info]:
    stages: List[_Stage_Info] = []
    last_stage = ""
    for index, row in data.iterrows():
        current_stage = EvaluationRunFLOpsProjectStage(
            row[FLOpsExclusiveCSVKeys.FLOPS_PROJECT_STAGE.value]
        )
        if last_stage == "":
            last_stage = current_stage
            stages.append(_Stage_Info(start=0, stage=current_stage))

        if last_stage != current_stage:
            last_stage = current_stage
            _last_stage = stages[-1]
            _last_stage.end = float(index)  # type: ignore
            next_stage = _Stage_Info(
                start=index,  # type: ignore
                stage=current_stage,
            )
            stages.append(next_stage)
    return stages


def _populate_stages_info_via_median(data: pd.DataFrame) -> List[_Stage_Info]:
    stages: List[_Stage_Info] = []
    median_stage_durations = get_median_stage_durations(get_stage_durations_df(data))
    for stage_enum in EvaluationRunFLOpsProjectStage:
        start = 0 if stages == [] else stages[-1].end
        median_duration = median_stage_durations.get(stage_enum.value)
        if median_duration is None:
            continue
        end = median_duration if stages == [] else stages[-1].end + median_duration
        stages.append(_Stage_Info(start=start, stage=stage_enum, end=end))
    return stages


def draw_stages(
    data: pd.DataFrame,
    color_intensity: float,
    stages_color_height: float = 100,
    use_median_stages: bool = False,
) -> None:
    from icecream import ic

    # ic(_populate_stages_info(data))
    # ic(_populate_stages_info_via_median(data))
    # return

    if use_median_stages:
        stages = _populate_stages_info_via_median(data)
    else:
        stages = _populate_stages_info(data)

    stages[-1].end = max(data.index)
    for stage_info in stages:
        plt.fill_between(
            (stage_info.start, stage_info.end),
            stages_color_height,
            color=sns.color_palette(
                palette="tab10",
                n_colors=len(list(EvaluationRunFLOpsProjectStage)),
            )[stage_info.stage.get_index()],
            alpha=color_intensity,
        )
        plt.axvline(
            x=stage_info.end,
            color="grey",
            linestyle="--",
            ymax=100,
        )

    original_handles, original_labels = plt.gca().get_legend_handles_labels()
    # Create a patch for each stage/color combination
    stage_names = [stage.value for stage in EvaluationRunFLOpsProjectStage]
    color_palette = sns.color_palette("tab10", n_colors=len(list(EvaluationRunFLOpsProjectStage)))

    stages_of_current_data = data[FLOpsExclusiveCSVKeys.FLOPS_PROJECT_STAGE.value].unique()
    new_patches = []
    for stage_name, color in zip(stage_names, color_palette):
        if stage_name not in stages_of_current_data:
            continue
        new_patches.append(
            Patch(
                facecolor=color,
                edgecolor="black",
                label=stage_name,
                alpha=color_intensity,
            )
        )
    combined_handles = original_handles + [patch for patch in new_patches]
    combined_labels = original_labels + [patch.get_label() for patch in new_patches]
    # Add the unified legend to the plot
    plt.gca().legend(
        handles=combined_handles, labels=combined_labels, bbox_to_anchor=(1, 1), loc="upper left"
    )


# def create_stage_color_palette(data: pd.DataFrame) -> List[str]
