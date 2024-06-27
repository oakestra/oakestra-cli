from typing import Optional

import typer
from typing_extensions import Annotated

from oak_cli.utils.typer_augmentations import AliasGroup
from oak_cli.worker.net_manager import get_net_manager_status, start_net_manager, stop_net_manager
from oak_cli.worker.node_engine import get_node_engine_status, start_node_engine, stop_node_engine

app = typer.Typer(cls=AliasGroup)


@app.command("start", help="Starts all worker components.")
def start_worker(
    use_debug_mode: Annotated[Optional[bool], typer.Option("-D")] = False,
    use_ml_data_server_for_flops_addon_learner: Annotated[
        Optional[bool], typer.Option("--ml_data_server_for_flops_addon_learner")
    ] = False,
) -> None:
    start_net_manager(use_debug_mode=use_debug_mode, background=True)
    start_node_engine(
        background=True,
        use_ml_data_server_for_flops_addon_learner=use_ml_data_server_for_flops_addon_learner,
    )


@app.command("status", help="Show the status of all worker components.")
def get_worker_components_status() -> None:
    get_net_manager_status()
    get_node_engine_status()


@app.command("stop", help="stops all worker components.")
def stop_worker_components() -> None:
    stop_net_manager()
    stop_node_engine()
