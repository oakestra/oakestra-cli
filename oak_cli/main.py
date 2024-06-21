#!/usr/bin/env python3
from importlib.metadata import version

import typer
from rich.console import Console
from rich.traceback import install

import oak_cli.addons.main as oak_addons
import oak_cli.apps.main as oak_applications
import oak_cli.configuration.main as oak_cli_configuration
import oak_cli.docker.main as oak_docker
import oak_cli.installer.main as oak_installer
import oak_cli.services.main as oak_services
from oak_cli.configuration.main import configuration_expansion_help_text
from oak_cli.utils.logging import logger
from oak_cli.utils.typer_augmentations import AliasGroup, typer_help_text

# https://rich.readthedocs.io/en/latest/traceback.html#traceback-handler
install(show_locals=True)
console = Console()

app = typer.Typer(
    help="Run Oakestra's CLI",
    context_settings={"help_option_names": ["-h", "--help"]},
    cls=AliasGroup,
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
    help="\n".join(
        (
            typer_help_text("docker(compose)"),
            configuration_expansion_help_text(configuration_cmd="oak c main-repo configure"),
        )
    ),
)
app.add_typer(
    typer_instance=oak_addons.app,
    name="addon",
    help=typer_help_text("addon"),
)
app.add_typer(
    typer_instance=oak_installer.app,
    name="installer",
    help="Install Oakestra dependencies & components.",
)
app.add_typer(
    typer_instance=oak_cli_configuration.app,
    name="c",
    help=typer_help_text("OAK CLI Configuration"),
)


@app.command("version, v", help="Shows the version of the currently installed OAK-CLI.")
def show_version():
    logger.info(f"OAK-CLI version: '{version('oak_cli')}'")


def main():
    app()


if __name__ == "__main__":
    main()
