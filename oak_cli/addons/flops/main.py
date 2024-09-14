import json
import pathlib

import typer

import oak_cli.utils.api.custom_requests as custom_requests
from oak_cli.addons.flops.SLAs.common import FLOpsSLAs
from oak_cli.addons.flops.SLAs.mocks.common import FLOpsMockDataProviderSLAs
from oak_cli.addons.flops.SLAs.projects.common import FLOpsProjectSLAs
from oak_cli.configuration.auxiliary import get_flops_addon_repo_path
from oak_cli.configuration.common import get_config_value
from oak_cli.configuration.keys.enums import ConfigurableConfigKey
from oak_cli.utils.api.custom_http import HttpMethod
from oak_cli.utils.common import run_in_shell
from oak_cli.utils.exceptions.types import OakCLIExceptionTypes
from oak_cli.utils.styling import create_spinner
from oak_cli.utils.typer_augmentations import AliasGroup


def get_root_fl_manager_url() -> str:
    return f"http://{get_config_value(ConfigurableConfigKey.SYSTEM_MANAGER_IP)}:5072"


app = typer.Typer(cls=AliasGroup)


def _load_sla(sla: FLOpsSLAs, sla_path: pathlib.Path) -> dict:
    with open(sla_path / f"{sla.value}.SLA.json", "r") as f:
        return json.load(f)


@app.command("project, p", help="Starts a new FLOps project.")
def create_new_flops_project(project_sla: FLOpsProjectSLAs) -> None:
    custom_requests.CustomRequest(
        custom_requests.RequestCore(
            http_method=HttpMethod.POST,
            base_url=get_root_fl_manager_url(),
            api_endpoint="/api/flops/projects",
            data=_load_sla(project_sla, FLOpsProjectSLAs.get_SLAs_path()),
        ),
        custom_requests.RequestAuxiliaries(
            what_should_happen=f"Init new FLOps project for SLA '{project_sla}'",
            show_msg_on_success=True,
            oak_cli_exception_type=OakCLIExceptionTypes.FLOPS_PLUGIN,
        ),
    ).execute()


@app.command("mock_data, m", help="Deploys a mock-data-provider.")
def create_new_mock_data_service(mock_sla: FLOpsMockDataProviderSLAs) -> None:
    custom_requests.CustomRequest(
        custom_requests.RequestCore(
            http_method=HttpMethod.POST,
            base_url=get_root_fl_manager_url(),
            api_endpoint="/api/flops/mocks",
            data=_load_sla(mock_sla, FLOpsMockDataProviderSLAs.get_SLAs_path()),
        ),
        custom_requests.RequestAuxiliaries(
            what_should_happen=f"Init new FLOps mock data service for SLA '{mock_sla}'",
            show_msg_on_success=True,
            oak_cli_exception_type=OakCLIExceptionTypes.FLOPS_PLUGIN,
        ),
    ).execute()


@app.command(
    "tracking, t",
    help="""
        Returns the URL of the tracking server of the specified customer.
        Deployes the Tracking Server Service if it is not yet deployed.
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
        (Only allowed if you are an Admin)
        Resets the FLOps Addon Database.
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


# TODO split this file up into multiple ones


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
    # TODO unify this compose path
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
