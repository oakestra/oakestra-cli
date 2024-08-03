import pandas as pd
import seaborn as sns

from oak_cli.evaluation.addons.flops.utils.draw import draw_graph
from oak_cli.evaluation.addons.flops.utils.keys import (
    CPU_KEY,
    DISK_START_KEY,
    MEMORY_KEY,
    RUN_ID_KEY,
    STAGE_KEY,
)


def draw_cpu_and_memory_linegraph(normalized_data: pd.DataFrame) -> None:
    draw_graph(
        title="Evaluation Runs Average",
        data=normalized_data[[CPU_KEY, MEMORY_KEY, STAGE_KEY, RUN_ID_KEY]],
        plot_functions=[
            lambda: sns.lineplot(data=normalized_data[[CPU_KEY, MEMORY_KEY, STAGE_KEY]])
        ],
        use_percentage_limits=True,
        y_label="Resource Usage (%)",
        show_stages=True,
        use_median_stages=True,
    )


def draw_disk_space_linegraph(normalized_data: pd.DataFrame) -> None:
    _normalized_df = normalized_data.copy()
    _normalized_df[[DISK_START_KEY]] = _normalized_df[[DISK_START_KEY]] / 1024
    draw_graph(
        title="Evaluation Runs Average",
        data=_normalized_df[[DISK_START_KEY, STAGE_KEY, RUN_ID_KEY]],
        plot_functions=[lambda: sns.lineplot(data=_normalized_df[[DISK_START_KEY, STAGE_KEY]])],
        y_label="Disk Space Change (GB)",
        x_lim=(0, max(_normalized_df.index)),
        y_lim=0,
        show_stages=True,
        use_median_stages=True,
    )
