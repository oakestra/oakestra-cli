import pandas as pd
import seaborn as sns

from oak_cli.evaluation.addons.flops.utils.draw import draw_graph
from oak_cli.evaluation.addons.flops.utils.keys import (
    ACCURACY_KEY,
    LOSS_KEY,
    TRAINED_MODEL_RUN_ID_KEY,
)


def draw_trained_model_comparison_graph(data: pd.DataFrame) -> None:
    _data = data.copy()
    _data[ACCURACY_KEY] = _data[ACCURACY_KEY] * 100
    _data[LOSS_KEY] = _data[LOSS_KEY] * 100
    melted_df = _data.melt(
        id_vars=TRAINED_MODEL_RUN_ID_KEY,
        value_vars=[ACCURACY_KEY, LOSS_KEY],
    )
    draw_graph(
        data=_data,
        x_label="Evaluation Run",
        y_label="Trained Model Metrics (%)",
        show_legend_in_right_bottom_corner=True,
        plot_functions=[
            lambda: sns.barplot(
                x=TRAINED_MODEL_RUN_ID_KEY,
                y="value",
                data=melted_df,
                hue="variable",
            )
        ],
    )
