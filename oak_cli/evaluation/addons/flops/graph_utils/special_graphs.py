from typing import Optional, Tuple, Union

import pandas as pd
import seaborn as sns

from oak_cli.evaluation.addons.flops.graph_utils.keys import (
    RUN_ID_KEY,
    STAGE_KEY,
    TIME_START_KEY,
    TRAINED_MODEL_RUN_ID_KEY,
)
from oak_cli.evaluation.addons.flops.graph_utils.main import draw_graph
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
    y_label: str,
    key: str,
    title: Optional[str] = "",
    y_lim: Optional[Union[Tuple[float, float], float]] = None,
    font_size_multiplier: float = 1,
    y_axis_font_size_multiplier: float = 1.5,
    x_axis_font_size_multiplier: Optional[float] = None,
) -> None:
    draw_graph(
        title=title,
        y_label=y_label,
        size=(30, 10),
        data=data,
        plot_functions=[
            lambda: sns.violinplot(
                x=STAGE_KEY,
                y=key,
                data=data,
                hue=STAGE_KEY,
                alpha=0.3,
                palette=PALETTE,
            ),
            lambda: sns.boxplot(
                x=STAGE_KEY,
                y=key,
                data=data,
                hue=STAGE_KEY,
                palette=PALETTE,
            ),
        ],
        y_lim=y_lim,
        font_size_multiplier=font_size_multiplier,
        y_axis_font_size_multiplier=y_axis_font_size_multiplier,
        x_axis_font_size_multiplier=x_axis_font_size_multiplier,
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
