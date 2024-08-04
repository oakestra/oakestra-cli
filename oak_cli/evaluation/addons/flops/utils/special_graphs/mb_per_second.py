import pandas as pd
import seaborn as sns

from oak_cli.evaluation.addons.flops.utils.draw import draw_graph
from oak_cli.evaluation.addons.flops.utils.keys import DISK_LAST_KEY, STAGE_KEY, TIME_START_KEY
from oak_cli.evaluation.addons.flops.utils.stages.auxiliary import get_stage_color_mapping


def draw_mb_per_second_graph(
    data: pd.DataFrame,
    use_bar_plot: bool = False,
    show_confidence_interval: bool = True,
) -> None:
    _data = data.copy()
    _data[["MB/s"]] = round(_data[[DISK_LAST_KEY]] / 5, 0)
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

    draw_graph(
        size=(15, 5),
        title="Singular Example Evaluation Run",
        data=_data,
        plot_functions=[draw_barplot if use_bar_plot else draw_boxplot],
        y_label="Disk Space Change Between Measurements (MB)",
    )
