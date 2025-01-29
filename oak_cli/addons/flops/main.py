import json
import pathlib

import typer

import oak_cli.utils.api.custom_requests as custom_requests
from oak_cli.addons.flops.auxiliary import get_flops_addon_repo_path
from oak_cli.addons.flops.SLAs.main import (
    OAK_CLI_FLOPS_MOCKS_SLA_FOLDER_PATH,
    OAK_CLI_FLOPS_PROJECT_SLA_FOLDER_PATH,
    get_sla_file_path,
)
from oak_cli.configuration.common import get_config_value
from oak_cli.configuration.keys.enums import ConfigurableConfigKey
from oak_cli.utils.api.custom_http import HttpMethod
from oak_cli.utils.common import print_sla, run_in_shell
from oak_cli.utils.exceptions.types import OakCLIExceptionTypes
from oak_cli.utils.styling import create_spinner
from oak_cli.utils.typer_augmentations import AliasGroup


def get_root_fl_manager_url() -> str:
    return f"http://{get_config_value(ConfigurableConfigKey.SYSTEM_MANAGER_IP)}:5072"


app = typer.Typer(cls=AliasGroup)


def _load_sla(sla_file_path: pathlib.Path) -> dict:
    with open(sla_file_path, "r") as f:
        return json.load(f)


@app.command("project, p", help="Start a new FLOps project")
def create_new_flops_project(
    project_sla_file_name: str = "",
    show: bool = typer.Option(False, help="Only display the SLA"),
) -> None:
    sla_file_path = get_sla_file_path(
        sla_file_name=project_sla_file_name,
        sla_folder=OAK_CLI_FLOPS_PROJECT_SLA_FOLDER_PATH,
    )
    if show:
        print_sla(sla_file_path)
        return

    custom_requests.CustomRequest(
        custom_requests.RequestCore(
            http_method=HttpMethod.POST,
            base_url=get_root_fl_manager_url(),
            api_endpoint="/api/flops/projects",
            data=_load_sla(sla_file_path),
        ),
        custom_requests.RequestAuxiliaries(
            what_should_happen=f"Init new FLOps project for SLA '{sla_file_path}'",
            show_msg_on_success=True,
            oak_cli_exception_type=OakCLIExceptionTypes.FLOPS_PLUGIN,
        ),
    ).execute()


@app.command("mock_data, m", help="Deploy a mock-data-provider")
def create_new_mock_data_service(
    mock_sla_file_name: str = "",
    show: bool = typer.Option(False, help="Only display the SLA"),
) -> None:
    sla_file_path = get_sla_file_path(
        sla_file_name=mock_sla_file_name,
        sla_folder=OAK_CLI_FLOPS_MOCKS_SLA_FOLDER_PATH,
    )
    if show:
        print_sla(sla_file_path)
        return

    custom_requests.CustomRequest(
        custom_requests.RequestCore(
            http_method=HttpMethod.POST,
            base_url=get_root_fl_manager_url(),
            api_endpoint="/api/flops/mocks",
            data=_load_sla(sla_file_path),
        ),
        custom_requests.RequestAuxiliaries(
            what_should_happen=f"Init a new FLOps mock data service for SLA '{sla_file_path}'",
            show_msg_on_success=True,
            oak_cli_exception_type=OakCLIExceptionTypes.FLOPS_PLUGIN,
        ),
    ).execute()


@app.command(
    "tracking, t",
    help="""
        Deploy the Tracking Server Service if it is not yet deployed

        Returns the URL of the tracking server of the specified customer
        """,
)
def get_tracking_url(customer_id: str = "Admin") -> None:
    custom_requests.CustomRequest(
        custom_requests.RequestCore(
            http_method=HttpMethod.GET,
            base_url=get_root_fl_manager_url(),
            api_endpoint="/api/flops/tracking",
            data={"customerID": customer_id},
        ),
        custom_requests.RequestAuxiliaries(
            what_should_happen="Get Tracking (Server) URL",
            show_msg_on_success=True,
            oak_cli_exception_type=OakCLIExceptionTypes.FLOPS_PLUGIN,
        ),
    ).execute()


@app.command(
    "reset-database, redb",
    help="""
        (Only allowed for Admins)
        Reset the FLOps Addon Database
        """,
)
def reset_database(customer_id: str = "Admin") -> None:
    custom_requests.CustomRequest(
        custom_requests.RequestCore(
            http_method=HttpMethod.DELETE,
            base_url=get_root_fl_manager_url(),
            api_endpoint="/api/flops/database",
            data={"customerID": customer_id},
        ),
        custom_requests.RequestAuxiliaries(
            what_should_happen="Reset the FLOps Database",
            show_msg_on_success=True,
            oak_cli_exception_type=OakCLIExceptionTypes.FLOPS_PLUGIN,
        ),
    ).execute()


# TODO(malyuka): split this file up into multiple ones


@app.command("restart-management, restart, re")
def restart_flops_manager() -> None:
    flops_compose = get_flops_addon_repo_path() / "docker" / "flops_management.docker_compose.yml"
    cmd = "&& ".join(
        (
            f"docker compose -f {flops_compose} down",
            f"docker compose -f {flops_compose} up --build -d",
        )
    )
    with create_spinner(message="Restarting FLOps Management (Docker Compose)'"):
        run_in_shell(shell_cmd=cmd, pure_shell=True)


@app.command("clear-registry")
def clear_registry() -> None:
    # TODO(malyuka): unify this compose path
    flops_compose = get_flops_addon_repo_path() / "docker" / "flops_management.docker_compose.yml"
    cmd = " ".join(
        (
            f"docker compose -f {flops_compose}",
            "exec flops_image_registry",
            "bash -c",
            "'rm -rf /var/lib/registry/*'",
        )
    )
    run_in_shell(shell_cmd=cmd, pure_shell=True)
