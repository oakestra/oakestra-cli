from typing import Dict, List, Tuple, Union

import pandas as pd
import seaborn as sns
from pydantic import BaseModel

from oak_cli.evaluation.addons.flops.main import (
    EvaluationRunFLOpsProjectStage,
    FLOpsExclusiveCSVKeys,
)
from oak_cli.evaluation.addons.flops.utils.stages.main import (
    get_median_stage_durations,
    get_stage_durations_df,
)


class _Stage_Info(BaseModel):
    stage: EvaluationRunFLOpsProjectStage
    start: float = 0
    end: float = 0


def populate_stages_info(
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


def populate_stages_info_via_median(data: pd.DataFrame) -> List[_Stage_Info]:
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


def get_stage_color_mapping(
    use_stage_names_as_keys: bool = False,
) -> Dict[Union[EvaluationRunFLOpsProjectStage, str], Tuple[float, float, float]]:
    def get_color(index: int) -> Tuple[float, float, float]:
        return sns.color_palette("tab10", 10)[index]

    mapping = {}
    for stage_enum in EvaluationRunFLOpsProjectStage:
        mapping[stage_enum.value if use_stage_names_as_keys else stage_enum] = get_color(
            stage_enum.get_index()
        )

    return mapping
