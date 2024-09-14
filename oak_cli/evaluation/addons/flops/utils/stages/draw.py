import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Patch

from oak_cli.evaluation.addons.flops.main import (
    EvaluationRunFLOpsProjectStage,
    FLOpsExclusiveCSVKeys,
)
from oak_cli.evaluation.addons.flops.utils.stages.auxiliary import (
    get_stage_color_mapping,
    populate_stages_info,
    populate_stages_info_via_median,
)


def draw_stages(
    data: pd.DataFrame,
    color_intensity: float,
    stages_color_height: float = 100,
    use_median_stages: bool = False,
    show_only_stage_legend: bool = False,
) -> None:
    if use_median_stages:
        stages = populate_stages_info_via_median(data)
    else:
        stages = populate_stages_info(data)

    stages[-1].end = max(data.index)
    if not show_only_stage_legend:
        for stage_info in stages:
            plt.fill_between(
                (stage_info.start, stage_info.end),
                stages_color_height,
                color=get_stage_color_mapping()[stage_info.stage],
                alpha=color_intensity,
            )
            plt.axvline(
                x=stage_info.end,
                color="grey",
                linestyle="--",
                ymax=100,
            )

    original_handles, original_labels = plt.gca().get_legend_handles_labels()
    stage_color_map = get_stage_color_mapping()

    stages_of_current_data = data[FLOpsExclusiveCSVKeys.FLOPS_PROJECT_STAGE.value].unique()
    new_patches = []
    for stage in EvaluationRunFLOpsProjectStage:
        if stage.value not in stages_of_current_data:
            continue
        new_patches.append(
            Patch(
                facecolor=stage_color_map[stage],
                edgecolor="black",
                label=stage.value,
                alpha=color_intensity,
            )
        )
    combined_handles = original_handles + [patch for patch in new_patches]
    combined_labels = original_labels + [patch.get_label() for patch in new_patches]
    plt.gca().legend(
        handles=combined_handles,
        labels=combined_labels,
        bbox_to_anchor=(1, 1),
        loc="upper left",
        # fontsize=14,
        fontsize=20,
    )
