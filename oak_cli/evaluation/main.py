import typer

import oak_cli.evaluation.machine as machine_evaluations
from oak_cli.utils.typer_augmentations import typer_help_text

app = typer.Typer()

app.add_typer(
    typer_instance=machine_evaluations.app,
    name="machine",
    help=typer_help_text("machine"),
)
