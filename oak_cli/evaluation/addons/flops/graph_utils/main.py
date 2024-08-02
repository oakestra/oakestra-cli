from typing import Callable, List, Optional, Tuple, Union

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from oak_cli.evaluation.addons.flops.graph_utils.stages import STAGE_ID_KEY, draw_stages
from oak_cli.evaluation.graph_utils import adjust_xticks, get_evaluation_run_duration_label

_DEFAULT_FONT_SIZE = 10


def draw_graph(
    data: pd.DataFrame,
    title: Optional[str] = "",
    plot_functions: Optional[List[Callable]] = None,
    x_lim: Optional[Union[Tuple[float, float], float]] = None,
    y_lim: Optional[Union[Tuple[float, float], float]] = None,
    x_label: str = "",
    y_label: str = "",
    size: Tuple[int, int] = (10, 5),
    show_stages: bool = False,
    stages_color_intensity: float = 0.3,
    stages_color_height: float = 100,
    use_percentage_limits: bool = False,
    font_size_multiplier: float = 1,
    y_axis_font_size_multiplier: Optional[float] = None,
    x_axis_font_size_multiplier: Optional[float] = None,
    sort_by_stage_id: bool = False,
    use_median_stages: bool = False,
) -> None:
    if sort_by_stage_id:
        data = data.copy().sort_values(by=STAGE_ID_KEY)
    fig, ax = plt.subplots(figsize=size)
    if title:
        ax.set_title(title)

    if not plot_functions:
        sns.lineplot(data=data)
    else:
        for plot_function in plot_functions:
            plot_function()

    x_font_size = _DEFAULT_FONT_SIZE * (x_axis_font_size_multiplier or font_size_multiplier)
    plt.xlabel(
        x_label or get_evaluation_run_duration_label(),
        fontsize=x_font_size,
    )
    plt.tick_params(axis="x", labelsize=x_font_size)
    adjust_xticks(ax)

    y_font_size = _DEFAULT_FONT_SIZE * (y_axis_font_size_multiplier or font_size_multiplier)
    plt.ylabel(
        y_label,
        fontsize=y_font_size,
    )
    plt.tick_params(axis="y", labelsize=y_font_size)

    if use_percentage_limits:
        if y_lim is None:
            y_lim = (0, 100)
        if x_lim is None:
            x_lim = (0, max(data.index))

    if x_lim is not None:
        if isinstance(x_lim, tuple):
            plt.xlim([x_lim[0], x_lim[1]])
        else:
            plt.xlim(x_lim)
    if y_lim is not None:
        if isinstance(y_lim, tuple):
            plt.ylim([y_lim[0], y_lim[1]])
        else:
            plt.ylim(y_lim)

    if show_stages:
        draw_stages(
            data=data,
            color_intensity=stages_color_intensity,
            stages_color_height=stages_color_height,
            use_median_stages=use_median_stages,
        )

    plt.show()
