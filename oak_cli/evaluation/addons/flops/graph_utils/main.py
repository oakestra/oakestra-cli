from typing import Callable, List, Optional, Tuple

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.patches import Patch
from pydantic import BaseModel

from oak_cli.evaluation.addons.flops.main import (
    EvaluationRunFLOpsProjectStage,
    FLOpsExclusiveCSVKeys,
)
from oak_cli.evaluation.graph_utils import adjust_xticks, get_evaluation_run_duration_label

_DEFAULT_FONT_SIZE = 10


class _Stage_Info(BaseModel):
    stage: EvaluationRunFLOpsProjectStage
    start: float = 0
    end: float = 0


def _draw_stages(
    data: pd.DataFrame,
    color_intensity: float,
    stages_color_height: float = 100,
) -> None:
    stages: List[_Stage_Info] = []
    last_stage = ""
    for index, row in data.iterrows():
        current_stage = EvaluationRunFLOpsProjectStage(
            row[FLOpsExclusiveCSVKeys.FLOPS_PROJECT_STAGE.value]
        )

        if last_stage == "":
            last_stage = current_stage
            stages.append(_Stage_Info(start=0, stage=current_stage))

        if last_stage != current_stage:
            last_stage = current_stage
            plt.axvline(
                x=index,  # type: ignore
                color="grey",
                linestyle="--",
                ymax=100,
            )
            _last_stage = stages[-1]
            _last_stage.end = float(index)  # type: ignore
            next_stage = _Stage_Info(
                start=index,  # type: ignore
                stage=current_stage,
            )
            stages.append(next_stage)

    stages[-1].end = max(data.index)
    for stage_info in stages:
        plt.fill_between(
            (stage_info.start, stage_info.end),
            stages_color_height,
            color=sns.color_palette(
                palette="tab10",
                n_colors=len(list(EvaluationRunFLOpsProjectStage)),
            )[stage_info.stage.get_index()],
            alpha=color_intensity,
        )

    original_handles, original_labels = plt.gca().get_legend_handles_labels()
    # Create a patch for each stage/color combination
    stage_names = [stage.value for stage in EvaluationRunFLOpsProjectStage]
    color_palette = sns.color_palette("tab10", n_colors=len(list(EvaluationRunFLOpsProjectStage)))

    stages_of_current_data = data[FLOpsExclusiveCSVKeys.FLOPS_PROJECT_STAGE.value].unique()
    new_patches = []
    for stage_name, color in zip(stage_names, color_palette):
        if stage_name not in stages_of_current_data:
            continue
        new_patches.append(
            Patch(
                facecolor=color,
                edgecolor="black",
                label=stage_name,
                alpha=color_intensity,
            )
        )

    combined_handles = original_handles + [
        patch for patch in new_patches
    ]  # Directly use Patch objects as handles
    combined_labels = original_labels + [
        patch.get_label() for patch in new_patches
    ]  # Retrieve labels from Patch objects
    # Add the unified legend to the plot
    plt.gca().legend(
        handles=combined_handles, labels=combined_labels, bbox_to_anchor=(1, 1), loc="upper left"
    )


def draw_graph(
    data: pd.DataFrame,
    title: Optional[str] = "",
    plot_functions: Optional[List[Callable]] = None,
    x_lim: Optional[Tuple[float, float]] = None,
    y_lim: Optional[Tuple[float, float]] = None,
    y_label: str = "Resource Usage (%)",
    size: Tuple[int, int] = (10, 5),
    show_stages: bool = False,
    stages_color_intensity: float = 0.3,
    stages_color_height: float = 100,
    use_percentage_limits: bool = False,
    font_size_multiplier: float = 1,
    y_axis_font_size_multiplier: Optional[float] = None,
    x_axis_font_size_multiplier: Optional[float] = None,
) -> None:
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
        get_evaluation_run_duration_label(),
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
        if not y_lim:
            y_lim = (0, 100)
        if not x_lim:
            x_lim = (0, max(data.index))

    if x_lim:
        plt.xlim([x_lim[0], x_lim[1]])
    if y_lim:
        plt.ylim([y_lim[0], y_lim[1]])
    else:
        plt.ylim(0)

    if show_stages:
        _draw_stages(
            data=data,
            color_intensity=stages_color_intensity,
            stages_color_height=stages_color_height,
        )

    plt.show()
