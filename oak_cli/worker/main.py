import typer

import oak_cli.worker.ctr
from oak_cli.utils.typer_augmentations import typer_help_text

app = typer.Typer()

app.add_typer(
    typer_instance=oak_cli.worker.ctr.app,
    name="ctr",
    help=typer_help_text("ctr"),
)
