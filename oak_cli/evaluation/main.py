import typer

import oak_cli.evaluation.localhost_resources.main as localhost_resources
from oak_cli.utils.typer_augmentations import typer_help_text

app = typer.Typer()

app.add_typer(
    typer_instance=localhost_resources.app,
    name="localhost",
    help=typer_help_text("localhost-resources"),
)
