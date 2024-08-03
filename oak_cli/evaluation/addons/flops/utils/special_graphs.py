from typing import Optional, Tuple, Union

import pandas as pd
import seaborn as sns

from oak_cli.evaluation.addons.flops.utils.draw import draw_graph
from oak_cli.evaluation.addons.flops.utils.keys import (
    RUN_ID_KEY,
    STAGE_KEY,
    TIME_START_KEY,
    TRAINED_MODEL_RUN_ID_KEY,
)
from oak_cli.evaluation.addons.flops.utils.stages.auxiliary import get_stage_color_mapping
from oak_cli.evaluation.addons.flops.utils.stages.main import STAGE_ID_KEY
from oak_cli.evaluation.graph_utils import PALETTE


def draw_line_graph_with_all_runs(
    data: pd.DataFrame,
    y_label: str,
    key: str,
    title: str = "All Evaluation Runs - Duration Diversity",
    font_size_multiplier: float = 1,
    y_axis_font_size_multiplier: Optional[float] = None,
    x_axis_font_size_multiplier: Optional[float] = None,
) -> None:
    draw_graph(
        title=title,
        y_label=y_label,
        size=(15, 8),
        data=data,
        plot_functions=[
            lambda: sns.lineplot(
                data=data,
                x=TIME_START_KEY,
                y=key,
                hue=RUN_ID_KEY,
            )
        ],
        use_percentage_limits=True,
        font_size_multiplier=font_size_multiplier,
        y_axis_font_size_multiplier=y_axis_font_size_multiplier,
        x_axis_font_size_multiplier=x_axis_font_size_multiplier,
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


def draw_trained_model_comparison_graph(
    data: pd.DataFrame,
    key: str,
    y_label: str,
    font_size_multiplier: float = 1,
    y_axis_font_size_multiplier: Optional[float] = None,
    x_axis_font_size_multiplier: Optional[float] = None,
) -> None:
    _data = data.copy()
    _data[key] = _data[key] * 100
    draw_graph(
        data=_data,
        y_label=y_label,
        plot_functions=[
            lambda: sns.barplot(
                x=TRAINED_MODEL_RUN_ID_KEY,
                y=key,
                data=_data,
                palette=PALETTE,
                hue=TRAINED_MODEL_RUN_ID_KEY,
                legend=False,
            )
        ],
        font_size_multiplier=font_size_multiplier,
        y_axis_font_size_multiplier=y_axis_font_size_multiplier,
        x_axis_font_size_multiplier=x_axis_font_size_multiplier,
    )
