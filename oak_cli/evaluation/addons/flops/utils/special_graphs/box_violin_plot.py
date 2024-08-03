from typing import Optional, Tuple, Union

import pandas as pd
import seaborn as sns

from oak_cli.evaluation.addons.flops.utils.draw import draw_graph
from oak_cli.evaluation.addons.flops.utils.keys import CPU_KEY, MEMORY_KEY, STAGE_KEY
from oak_cli.evaluation.addons.flops.utils.stages.auxiliary import get_stage_color_mapping
from oak_cli.evaluation.addons.flops.utils.stages.main import STAGE_ID_KEY


def draw_box_violin_plot_for_each_stage_for_cpu(data: pd.DataFrame) -> None:
    draw_box_violin_plot_for_each_stage(
        data=data,
        key=CPU_KEY,
        x_label="CPU Usage (%)",
    )


def draw_box_violin_plot_for_each_stage_for_memory(data: pd.DataFrame) -> None:
    draw_box_violin_plot_for_each_stage(
        data=data,
        key=MEMORY_KEY,
        x_label="Memory Usage (%)",
        x_lim=(40, 80),
    )


def draw_box_violin_plot_for_each_stage(
    data: pd.DataFrame,
    key: str,
    x_label: str = "",
    y_label: str = "",
    title: Optional[str] = "",
    x_lim: Optional[Union[Tuple[float, float], float]] = (0, 100),
    y_lim: Optional[Union[Tuple[float, float], float]] = None,
    font_size_multiplier: float = 1,
    y_axis_font_size_multiplier: float = 1,
    x_axis_font_size_multiplier: Optional[float] = None,
) -> None:
    data = data.copy().sort_values(by=STAGE_ID_KEY)
    stage_color_map = get_stage_color_mapping(use_stage_names_as_keys=True)
    draw_graph(
        title=title,
        x_label=x_label,
        y_label=y_label,
        size=(10, 8),
        data=data,
        plot_functions=[
            lambda: sns.violinplot(
                x=key,
                y=STAGE_KEY,
                data=data,
                hue=STAGE_KEY,
                alpha=0.3,
                palette=stage_color_map,
            ),
            lambda: sns.boxplot(
                x=key,
                y=STAGE_KEY,
                data=data,
                hue=STAGE_KEY,
                palette=stage_color_map,
            ),
        ],
        x_lim=x_lim,
        y_lim=y_lim,
        font_size_multiplier=font_size_multiplier,
        y_axis_font_size_multiplier=y_axis_font_size_multiplier,
        x_axis_font_size_multiplier=x_axis_font_size_multiplier,
        sort_by_stage_id=True,
    )
