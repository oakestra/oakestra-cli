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
import oak_cli.worker.main as oak_worker
from oak_cli.configuration.common import check_and_handle_config_file, get_config_value
from oak_cli.configuration.keys.enums import ConfigurableConfigKey
from oak_cli.configuration.local_machine_purpose import (
    LocalMachinePurpose,
    check_if_local_machine_has_required_purposes,
)
from oak_cli.utils.logging import logger
from oak_cli.utils.typer_augmentations import AliasGroup, typer_help_text

# https://rich.readthedocs.io/en/latest/traceback.html#traceback-handler
install(show_locals=True)
console = Console()

app = typer.Typer(
    help=" ".join(
        (
            "Run Oakestra's CLI.",
            "Many commands are hidden initially to avoid overwhelming new users"
            "and to focus on the reasonable commands for the current configuration.",
            "New commands can be un-locked by configuring your OAK-CLI installation further.",
            "If you want to unlock all capabilities of the CLI,"
            "configure the purpose for this machine as 'everything'.",
        )
    ),
    context_settings={"help_option_names": ["-h", "--help"]},
    cls=AliasGroup,
)

if check_if_local_machine_has_required_purposes(
    required_purposes=[LocalMachinePurpose.ROOT_ORCHESTRATOR]
):
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

if check_if_local_machine_has_required_purposes(
    required_purposes=[
        LocalMachinePurpose.DEVELOPMENT,
    ]
):
    app.add_typer(
        typer_instance=oak_docker.app,
        name="d",
        help=typer_help_text("docker(compose)"),
    )

if check_if_local_machine_has_required_purposes(
    required_purposes=[LocalMachinePurpose.ADDON_SUPPORT]
):
    app.add_typer(
        typer_instance=oak_addons.app,
        name="addon",
        help=typer_help_text("addon"),
    )

if check_if_local_machine_has_required_purposes(
    required_purposes=[LocalMachinePurpose.WORKER_NODE]
):
    app.add_typer(
        typer_instance=oak_worker.app,
        name="w",
        help=typer_help_text("Worker"),
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


@app.command("api-docs", help="Shows a links to the Swagger api-docs for Oakestra.")
def show_api_docs():
    check_and_handle_config_file()
    api_docs_link = (
        f"http://{get_config_value(ConfigurableConfigKey.SYSTEM_MANAGER_IP)}:1000/api/docs"
    )
    logger.info(f"Oakestra root API docs: '{api_docs_link}'")


def main():
    app()


if __name__ == "__main__":
    main()
