import pandas as pd
import seaborn as sns

from oak_cli.evaluation.addons.flops.utils.draw import draw_graph
from oak_cli.evaluation.addons.flops.utils.keys import CPU_KEY, MEMORY_KEY, RUN_ID_KEY, STAGE_KEY


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
