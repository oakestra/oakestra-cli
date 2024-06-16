#!/usr/bin/env python3
import typer
from rich.console import Console
from rich.traceback import install

import oak_cli.addons.main as oak_addons
import oak_cli.apps.main as oak_applications
import oak_cli.docker.main as oak_docker
import oak_cli.services.main as oak_services
from oak_cli.utils.typer_augmentations import typer_help_text

# https://rich.readthedocs.io/en/latest/traceback.html#traceback-handler
install(show_locals=True)
console = Console()

app = typer.Typer(
    help="Run Oakestra's CLI",
    context_settings={"help_option_names": ["-h", "--help"]},
)
app.add_typer(
    typer_instance=oak_applications.app,
    name="a",
    help=typer_help_text("application"),
)
app.add_typer(
    typer_instance=oak_services.app,
    name="s",
    help=typer_help_text("service"),
)
app.add_typer(
    typer_instance=oak_docker.app,
    name="d",
    help=typer_help_text("docker(compose)"),
)
app.add_typer(
    typer_instance=oak_addons.app,
    name="ad",
    help=typer_help_text("addon"),
)


def main():
    app()


if __name__ == "__main__":
    main()
