from __future__ import annotations

import glob
import pathlib
from typing import NamedTuple, Optional

import pandas as pd
from icecream import ic
from pandas.core.groupby import DataFrameGroupBy

from oak_cli.evaluation.addons.flops.main import EvaluationRunFLOpsProjectStage
from oak_cli.evaluation.addons.flops.utils.auxiliary import normalize_df_time_ranges
from oak_cli.evaluation.addons.flops.utils.keys import (
    NODE_KEY,
    NODE_ROOT,
    RUN_ID_KEY,
    STAGE_KEY,
    TIME_START_KEY,
    Cluster,
)
from oak_cli.evaluation.addons.flops.utils.main import Evaluation
from oak_cli.evaluation.addons.flops.utils.stages.main import STAGE_ID_KEY
from oak_cli.evaluation.graph_utils import ROUNDING_PRECISION


class PreparedDataFrames(NamedTuple):
    df: pd.DataFrame
    normalized_df: pd.DataFrame
    singular_run_df: pd.DataFrame

    trained_models_df: pd.DataFrame


def _concat_csvs(csv_files: list) -> pd.DataFrame:
    return pd.concat([pd.read_csv(file) for file in csv_files], ignore_index=True)


def _handle_cluster_csvs(csv_dir_path: pathlib.Path, cluster: Cluster) -> pd.DataFrame:
    cluster_csv_files = glob.glob(f"{csv_dir_path}/{cluster.value}/evaluation_run_*.csv")
    cluster_df = _concat_csvs(cluster_csv_files)
    # NOTE: The clusters lack correct stage information - only the root recorded it.
    # cluster_df.drop(STAGE_KEY, axis=1, inplace=True)
    cluster_df[NODE_KEY] = cluster.value
    return cluster_df


def _update_cluster_stages(group: DataFrameGroupBy) -> Optional[DataFrameGroupBy]:
    # Check if any row in the group has Node == Root
    if (group[NODE_KEY] == NODE_ROOT).any():  # type: ignore
        # Get the FLOps Project Stage value for the row with Node == Root
        stage_for_root = group.loc[group[NODE_KEY] == NODE_ROOT, STAGE_KEY].values[0]
        # Set the FLOps Project Stage value for all rows in the group to the value for Root
        group.loc[:, STAGE_KEY] = stage_for_root  # type: ignore
        return group
    # Sometimes the Root-Node value is missing (for what ever reason)
    # Simply drop time-stamps without root values.
    return None


def load_and_prepare_data(
    evaluation: Optional[Evaluation] = None,
    multi_cluster: bool = False,
) -> PreparedDataFrames:
    if evaluation:
        evaluations_root = pathlib.Path(__file__).parents[1] / "evaluations"
        csv_dir_name = f"{evaluation.value}_{evaluation.name.lower()}"
        csv_dir_path = evaluations_root / csv_dir_name / "csvs"
    else:
        csv_dir_path = pathlib.Path.cwd().parent / "csvs"

    if not multi_cluster:
        csv_files = glob.glob(f"{csv_dir_path}/evaluation_run_*.csv")
        df = _concat_csvs(csv_files)
        trained_models_df = pd.read_csv(csv_dir_path / "trained_models.csv")
    else:
        cluster_a_df = _handle_cluster_csvs(csv_dir_path=csv_dir_path, cluster=Cluster.CLUSTER_A)
        cluster_b_df = _handle_cluster_csvs(csv_dir_path=csv_dir_path, cluster=Cluster.CLUSTER_B)

        root_csv_files = glob.glob(f"{csv_dir_path}/root_node/evaluation_run_*.csv")
        root_df = _concat_csvs(root_csv_files)
        root_df[NODE_KEY] = NODE_ROOT

        df = pd.concat([root_df, cluster_a_df, cluster_b_df])

        trained_models_df = pd.read_csv(csv_dir_path / "root_node" / "trained_models.csv")

    # NOTE: The CSV "time-since-start" values are very precise,
    # thus they differ (slightly) between Evaluation-Runs.
    # This difference leads to issues when trying to plot them in an aggregated way.
    # To fix this we cast the floats to ints instead.
    # I.e. we are looking at whole seconds - which is fine for this concrete use-case.
    df[[TIME_START_KEY]] = round(df[[TIME_START_KEY]].astype(int) / 60, ROUNDING_PRECISION)

    if multi_cluster:
        df = df.groupby(TIME_START_KEY).apply(_update_cluster_stages)  # type: ignore

    # Add a numerical stage ID (instead of the string) for future numerical manipulations.
    df[STAGE_ID_KEY] = df[STAGE_KEY].apply(
        lambda stage_name: EvaluationRunFLOpsProjectStage(stage_name).get_index()
    )

    df.set_index(TIME_START_KEY, inplace=True)

    return PreparedDataFrames(
        df=df,
        normalized_df=normalize_df_time_ranges(df),
        # NOTE: The singular run is the middle run.
        # If the cycle had 10 runs it picks the 5th one.
        singular_run_df=df[df[RUN_ID_KEY] == (df[RUN_ID_KEY].max() // 2)],
        trained_models_df=trained_models_df,
    )
