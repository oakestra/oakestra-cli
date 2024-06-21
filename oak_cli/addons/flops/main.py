import json
import os
import pathlib
from typing import Optional

import typer
from icecream import ic

import oak_cli.utils.api.custom_requests as custom_requests
from oak_cli.addons.flops.SLAs.common import FLOpsSLAs
from oak_cli.addons.flops.SLAs.mocks.common import FLOpsMockDataProviderSLAs
from oak_cli.addons.flops.SLAs.projects.common import FLOpsProjectSLAs
from oak_cli.utils.api.custom_http import HttpMethod
from oak_cli.utils.exceptions.types import OakCLIExceptionTypes
from oak_cli.utils.typer_augmentations import AliasGroup

ROOT_FL_MANAGER_URL = f"http://{os.environ.get('SYSTEM_MANAGER_URL')}:5072"

app = typer.Typer(cls=AliasGroup)


def _load_sla(sla: FLOpsSLAs, sla_path: pathlib.Path) -> dict:
    with open(sla_path / f"{sla.value}.SLA.json", "r") as f:
        return json.load(f)


@app.command("project, p", help="Starts a new FLOps project.")
def create_new_flops_project(project_sla: FLOpsProjectSLAs) -> None:
    custom_requests.CustomRequest(
        custom_requests.RequestCore(
            http_method=HttpMethod.POST,
            base_url=ROOT_FL_MANAGER_URL,
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
            base_url=ROOT_FL_MANAGER_URL,
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
def get_tracking_url(customer_id: Optional[str] = "Admin") -> None:
    result = custom_requests.CustomRequest(
        custom_requests.RequestCore(
            http_method=HttpMethod.GET,
            base_url=ROOT_FL_MANAGER_URL,
            api_endpoint="/api/flops/tracking",
            data={"customerID": customer_id},
        ),
        custom_requests.RequestAuxiliaries(
            what_should_happen="Get Tracking (Server) URL",
            show_msg_on_success=True,
            oak_cli_exception_type=OakCLIExceptionTypes.FLOPS_PLUGIN,
        ),
    ).execute()
    ic(result)
