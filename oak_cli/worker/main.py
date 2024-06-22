import typer

import oak_cli.worker.ctr
import oak_cli.worker.net_manager
import oak_cli.worker.node_engine
from oak_cli.utils.typer_augmentations import typer_help_text
from oak_cli.worker.net_manager import NET_MANAGER_NAME
from oak_cli.worker.node_engine import NODE_ENGINE_NAME

app = typer.Typer()

app.add_typer(
    typer_instance=oak_cli.worker.ctr.app,
    name="ctr",
    help=typer_help_text("ctr"),
)

app.add_typer(
    typer_instance=oak_cli.worker.net_manager.app,
    name="net-manager",
    help=typer_help_text(NET_MANAGER_NAME),
)

app.add_typer(
    typer_instance=oak_cli.worker.node_engine.app,
    name="node-engine",
    help=typer_help_text(NODE_ENGINE_NAME),
)
