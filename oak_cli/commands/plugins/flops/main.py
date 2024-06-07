import json
import os
import pathlib

from icecream import ic

import oak_cli.utils.api.custom_requests as custom_requests
from oak_cli.commands.plugins.flops.SLAs.common import FLOpsSLAs
from oak_cli.commands.plugins.flops.SLAs.mocks.common import FLOpsMockDataProviderSLAs
from oak_cli.commands.plugins.flops.SLAs.projects.common import FLOpsProjectSLAs
from oak_cli.utils.api.custom_http import HttpMethod
from oak_cli.utils.exceptions.types import OakCLIExceptionTypes

ROOT_FL_MANAGER_URL = f"http://{os.environ.get('SYSTEM_MANAGER_URL')}:5072"


def _load_sla(sla: FLOpsSLAs, sla_path: pathlib.Path) -> dict:
    with open(sla_path / f"{sla.value}.SLA.json", "r") as f:
        return json.load(f)


def create_new_flops_project(sla: FLOpsProjectSLAs) -> None:
    custom_requests.CustomRequest(
        custom_requests.RequestCore(
            http_method=HttpMethod.POST,
            base_url=ROOT_FL_MANAGER_URL,
            api_endpoint="/api/flops/projects",
            data=_load_sla(sla, FLOpsProjectSLAs.get_SLAs_path()),
        ),
        custom_requests.RequestAuxiliaries(
            what_should_happen=f"Init new FLOps project for SLA '{sla}'",
            show_msg_on_success=True,
            oak_cli_exception_type=OakCLIExceptionTypes.FLOPS_PLUGIN,
        ),
    ).execute()


def create_new_mock_data_service(sla: FLOpsMockDataProviderSLAs) -> None:
    custom_requests.CustomRequest(
        custom_requests.RequestCore(
            http_method=HttpMethod.POST,
            base_url=ROOT_FL_MANAGER_URL,
            api_endpoint="/api/flops/mocks",
            data=_load_sla(sla, FLOpsMockDataProviderSLAs.get_SLAs_path()),
        ),
        custom_requests.RequestAuxiliaries(
            what_should_happen=f"Init new FLOps mock data service for SLA '{sla}'",
            show_msg_on_success=True,
            oak_cli_exception_type=OakCLIExceptionTypes.FLOPS_PLUGIN,
        ),
    ).execute()


def get_tracking_url() -> None:
    result = custom_requests.CustomRequest(
        custom_requests.RequestCore(
            http_method=HttpMethod.GET,
            base_url=ROOT_FL_MANAGER_URL,
            api_endpoint="/api/flops/tracking",
            data={"customerID": "Admin"},
        ),
        custom_requests.RequestAuxiliaries(
            what_should_happen="Get Tracking (Server) URL",
            show_msg_on_success=True,
            oak_cli_exception_type=OakCLIExceptionTypes.FLOPS_PLUGIN,
        ),
    ).execute()
    ic(result)
