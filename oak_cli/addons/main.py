import typer

import oak_cli.addons.flops.main as flops_addon
from oak_cli.utils.typer_augmentations import typer_help_text

app = typer.Typer()

app.add_typer(
    typer_instance=flops_addon.app,
    name="flops",
    help=typer_help_text("FLOps - Federated Learning Operations"),
)
