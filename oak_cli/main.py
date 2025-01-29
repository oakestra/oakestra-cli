#!/usr/bin/env python3
from importlib.metadata import version

import typer
from rich.console import Console
from rich.traceback import install

import oak_cli.addons.main as oak_addons
import oak_cli.apps.main as oak_applications
import oak_cli.configuration.main as oak_cli_configuration
import oak_cli.docker.main as oak_docker
import oak_cli.explanations.main as oak_explanations
import oak_cli.installer.main as oak_installer
import oak_cli.services.main as oak_services
import oak_cli.worker.main as oak_worker
from oak_cli.configuration.common import check_and_handle_config_file, get_config_value
from oak_cli.configuration.keys.enums import ConfigurableConfigKey
from oak_cli.configuration.local_machine_purpose.main import (
    LocalMachinePurpose,
    check_if_local_machine_has_required_purposes,
)
from oak_cli.initial import handle_init_use
from oak_cli.utils.ascii.main import print_oakestra_logo
from oak_cli.utils.consts import DOCS_LINK
from oak_cli.utils.logging import logger
from oak_cli.utils.typer_augmentations import AliasGroup, typer_help_text

# https://rich.readthedocs.io/en/latest/traceback.html#traceback-handler
install(show_locals=True)
console = Console()

app = typer.Typer(
    context_settings={"help_option_names": ["-h", "--help"]},
    cls=AliasGroup,
    help=f"The documentation is available here: {DOCS_LINK}",
)

if check_if_local_machine_has_required_purposes(
    required_purposes=[LocalMachinePurpose.ROOT_ORCHESTRATOR], initial_purpose_support=True
):
    app.add_typer(
        typer_instance=oak_applications.app,
        name="application, app, a",
        help=typer_help_text("application"),
    )
    app.add_typer(
        typer_instance=oak_services.app,
        name="service, s",
        help=typer_help_text("service"),
    )

if check_if_local_machine_has_required_purposes(
    required_purposes=[
        LocalMachinePurpose.DEVELOPMENT,
    ]
):
    app.add_typer(
        typer_instance=oak_docker.app,
        name="docker, d",
        help=typer_help_text("docker(compose)"),
    )

    # TODO(malyuka): Need to review/discuss if this is actually something we want as part of the CLI.
    # app.add_typer(
    #     typer_instance=oak_evaluation.app,
    #     name="evaluate",
    #     help=typer_help_text("evaluation"),
    # )

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
        name="worker, w",
        help=typer_help_text("Worker"),
    )


app.add_typer(
    typer_instance=oak_installer.app,
    name="installer, i",
    help="Install Oakestra dependencies & components",
)
app.add_typer(
    typer_instance=oak_cli_configuration.app,
    name="configuration, c",
    help=typer_help_text("OAK CLI Configuration"),
)


@app.command("version, v", help="Show the version of the currently installed OAK-CLI")
def show_version(show_logo: bool = True):
    if show_logo:
        print_oakestra_logo()
    logger.info(f"OAK-CLI version: '{version('oak_cli')}'")


@app.command("api-docs", help="Show a link to the Swagger api-docs for Oakestra")
def show_api_docs():
    check_and_handle_config_file()
    api_docs_link = (
        f"http://{get_config_value(ConfigurableConfigKey.SYSTEM_MANAGER_IP)}:10000/api/docs"
    )
    logger.info(f"Oakestra root API docs: '{api_docs_link}'")


@app.command("dashboard-link", help="Show a link to the Oakestra Dashboard GUI")
def show_dashboard_link():
    check_and_handle_config_file()
    dashboard_link = f"http://{get_config_value(ConfigurableConfigKey.SYSTEM_MANAGER_IP)}"
    logger.info(f"Oakestra Dashboard URL: '{dashboard_link}'")


app.add_typer(
    typer_instance=oak_explanations.app,
    name="explain, e",
    help="Explain the basics of the OAK-CLI and how to configure it",
)


def main():
    handle_init_use()
    app()


if __name__ == "__main__":
    main()
