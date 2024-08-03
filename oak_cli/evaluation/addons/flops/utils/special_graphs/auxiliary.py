from typing import Optional

import pandas as pd
import seaborn as sns

from oak_cli.evaluation.addons.flops.utils.draw import draw_graph
from oak_cli.evaluation.addons.flops.utils.keys import RUN_ID_KEY, TIME_START_KEY


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
