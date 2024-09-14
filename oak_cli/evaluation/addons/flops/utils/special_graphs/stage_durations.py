import pandas as pd
import seaborn as sns

from oak_cli.evaluation.addons.flops.utils.draw import draw_graph
from oak_cli.evaluation.addons.flops.utils.stages.auxiliary import (
    get_stage_color_mapping,
    get_stage_durations_df,
)
from oak_cli.evaluation.addons.flops.utils.stages.main import STAGE_DURATIONS_KEY, STAGE_KEY


def draw_stage_durations_graph(data: pd.DataFrame) -> None:
    _data = get_stage_durations_df(data)
    stage_color_map = get_stage_color_mapping(use_stage_names_as_keys=True)
    draw_graph(
        data=_data,
        plot_functions=[
            lambda: sns.barplot(
                data=_data,
                x=STAGE_DURATIONS_KEY,
                y=STAGE_KEY,
                palette=stage_color_map,
                hue=STAGE_KEY,
            )
        ],
        title="FLOps Project Stage Durations",
    )
