import glob
import pathlib
import sys

import pandas as pd
import seaborn as sns
from icecream import ic

from oak_cli.evaluation.addons.flops.graph_utils.keys import (
    ACCURACY_KEY,
    CPU_KEY,
    DISK_LAST_KEY,
    DISK_START_KEY,
    LOSS_KEY,
    MEMORY_KEY,
    NETWORK_LAST_KEYS,
    NETWORK_START_KEYS,
    RUN_ID_KEY,
    STAGE_KEY,
    TIME_START_KEY,
)
from oak_cli.evaluation.addons.flops.graph_utils.main import (
    STAGE_ID_KEY,
    draw_graph,
    normalize_df_time_ranges,
)
from oak_cli.evaluation.addons.flops.graph_utils.special_graphs import (
    draw_box_violin_plot_for_each_stage,
    draw_line_graph_with_all_runs,
    draw_trained_model_comparison_graph,
)
from oak_cli.evaluation.addons.flops.graph_utils.stages import (
    STAGE_DURATIONS_KEY,
    get_stage_durations_df,
)
from oak_cli.evaluation.addons.flops.main import EvaluationRunFLOpsProjectStage
from oak_cli.evaluation.graph_utils import PALETTE, ROUNDING_PRECISION
from oak_cli.utils.logging import logger
