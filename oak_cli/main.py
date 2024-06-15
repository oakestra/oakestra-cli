#!/usr/bin/env python3
import typer

import oak_cli.apps.main as oak_applications
import oak_cli.commands.docker.main as oak_docker
import oak_cli.services.main as oak_services
from oak_cli.utils.exceptions.main import OakCLIException
from oak_cli.utils.logging import logger
from oak_cli.utils.typer_augmentations import typer_help_text

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
    help=typer_help_text("docker"),
)


def main():
    try:
        app()
    except OakCLIException as e:
        logger.exception(f"{e.message}, {e.http_status}")
    except Exception:
        logger.exception("Unexpected exception occurred.")


if __name__ == "__main__":
    main()
