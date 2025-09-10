import json
from typing import List, Optional, TextIO

import typer
from icecream import ic
from typing_extensions import Annotated

from oak_cli.clusters.auxiliary import generate_current_cluster_table, generate_cluster_detail_table
from oak_cli.utils.logging import logger
from oak_cli.utils.styling import display_table
from oak_cli.utils.typer_augmentations import AliasGroup
from oak_cli.utils.types import LIVE_VIEW_FLAG_TYPE, VERBOSITY_FLAG_TYPE, ClusterName, Cluster


app = typer.Typer(cls=AliasGroup)

ALL_CLUSTERS_FLAG_TYPE = Annotated[
    bool,
    typer.Option(
        "-all", help="Show all registered clusters, including those not currently connected."
    ),
]


@app.command("list, ls", help="Show connected clusters")
def show_current_clusters(
    live: LIVE_VIEW_FLAG_TYPE = False,
    all: ALL_CLUSTERS_FLAG_TYPE = False,
) -> List[Cluster]:
    display_table(
        live,
        table_generator=lambda: generate_current_cluster_table(
            all=all,
            live=live,
        ),
    )


@app.command("info, i", help="Check details of a specific cluster")
def show_cluster_info(
    cluster_name: ClusterName,
    live: LIVE_VIEW_FLAG_TYPE = False,
) -> List[dict]:
    display_table(
        live,
        table_generator=lambda: generate_cluster_detail_table(
            name=cluster_name,
            live=live,
        ),
    )
