#!/usr/bin/env python3
import typer

import oak_cli.apps.main as oak_applications
import oak_cli.commands.services.main as oak_services
from oak_cli.utils.exceptions.main import OakCLIException
from oak_cli.utils.logging import logger


def _help_text(subject: str) -> str:
    return f"Command for {subject} related activities."


app = typer.Typer(
    help="Run Oakestra's CLI",
    context_settings={"help_option_names": ["-h", "--help"]},
)
app.add_typer(
    typer_instance=oak_applications.app,
    name="a",
    help=_help_text("application"),
)
app.add_typer(
    typer_instance=oak_services.app,
    name="s",
    help=_help_text("service"),
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
