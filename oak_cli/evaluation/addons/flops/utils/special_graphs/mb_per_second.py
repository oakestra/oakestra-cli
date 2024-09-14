from typing import Optional, Tuple, Union

import pandas as pd
import seaborn as sns

from oak_cli.evaluation.addons.flops.utils.draw import draw_graph
from oak_cli.evaluation.addons.flops.utils.keys import STAGE_KEY, TIME_START_KEY
from oak_cli.evaluation.addons.flops.utils.stages.auxiliary import get_stage_color_mapping
from oak_cli.evaluation.common import SCRAPE_INTERVAL


def draw_mb_per_second_graph(
    key: str,
    y_label: str,
    data: pd.DataFrame,
    use_bar_plot: bool = False,
    show_confidence_interval: bool = True,
    y_lim: Optional[Union[Tuple[float, float], float]] = None,
) -> None:
    _data = data.copy()
    _data[["MB/s"]] = round(_data[[key]] / SCRAPE_INTERVAL, 0)
    _data.reset_index(inplace=True)
    _data[TIME_START_KEY] = round(_data[TIME_START_KEY]).astype(int)
    _data.set_index(TIME_START_KEY, inplace=True)

    stage_color_map = get_stage_color_mapping(use_stage_names_as_keys=True)

    x_axis_color_mapping = {}
    for i, row in _data.iterrows():
        color = stage_color_map[row[STAGE_KEY]]
        x_axis_color_mapping[str(i)] = color

    def draw_barplot() -> None:
        sns.barplot(
            data=_data,
            x=TIME_START_KEY,
            y="MB/s",
            palette=x_axis_color_mapping,
            ci=95 if show_confidence_interval else None,
        )

    def draw_boxplot() -> None:
        sns.boxplot(
            data=_data,
            x=TIME_START_KEY,
            y="MB/s",
            palette=x_axis_color_mapping,
        )

    def draw_violinplot() -> None:
        sns.violinplot(
            data=_data,
            x=TIME_START_KEY,
            y="MB/s",
            palette=x_axis_color_mapping,
            alpha=0.3,
        )

    draw_graph(
        size=(15, 5),
        title="Singular Example Evaluation Run",
        data=_data,
        plot_functions=[draw_barplot] if use_bar_plot else [draw_violinplot, draw_boxplot],
        y_label=y_label,
        y_lim=y_lim,
        show_only_stage_legend=True,
    )
