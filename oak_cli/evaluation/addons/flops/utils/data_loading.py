import glob
import pathlib
from typing import NamedTuple

import pandas as pd

from oak_cli.evaluation.addons.flops.main import EvaluationRunFLOpsProjectStage
from oak_cli.evaluation.addons.flops.utils.auxiliary import normalize_df_time_ranges
from oak_cli.evaluation.addons.flops.utils.keys import RUN_ID_KEY, STAGE_KEY, TIME_START_KEY
from oak_cli.evaluation.addons.flops.utils.main import Evaluation
from oak_cli.evaluation.addons.flops.utils.stages.main import STAGE_ID_KEY
from oak_cli.evaluation.graph_utils import ROUNDING_PRECISION


class PreparedDataFrames(NamedTuple):
    df: pd.DataFrame
    normalized_df: pd.DataFrame
    singular_run_df: pd.DataFrame

    trained_models_df: pd.DataFrame


def load_and_prepare_data(evaluation: Evaluation) -> PreparedDataFrames:
    evaluations_root = pathlib.Path(__file__).parents[1] / "evaluations"
    csv_dir_name = f"{evaluation.value}_{evaluation.name.lower()}"
    csv_dir_path = evaluations_root / csv_dir_name / "csvs"
    csv_files = glob.glob(f"{csv_dir_path}/evaluation_run_*.csv")

    df = pd.concat([pd.read_csv(file) for file in csv_files], ignore_index=True)

    # Add a numerical stage ID (instead of the string) for future numerical manipulations.
    df[STAGE_ID_KEY] = df[STAGE_KEY].apply(
        lambda stage_name: EvaluationRunFLOpsProjectStage(stage_name).get_index()
    )

    # NOTE: The CSV "time-since-start" values are very precise,
    # thus they differ (slightly) between Evaluation-Runs.
    # This difference leads to issues when trying to plot them in an aggregated way.
    # To fix this we cast the floats to ints instead.
    # I.e. we are looking at whole seconds - which is fine for this concrete use-case.
    df[[TIME_START_KEY]] = round(df[[TIME_START_KEY]].astype(int) / 60, ROUNDING_PRECISION)

    df.set_index(TIME_START_KEY, inplace=True)

    return PreparedDataFrames(
        df=df,
        normalized_df=normalize_df_time_ranges(df),
        # NOTE: The singular run is the middle run.
        # If the cycle had 10 runs it picks the 5th one.
        singular_run_df=df[df[RUN_ID_KEY] == (df[RUN_ID_KEY].max() // 2)],
        trained_models_df=pd.read_csv(csv_dir_path / "trained_models.csv"),
    )
