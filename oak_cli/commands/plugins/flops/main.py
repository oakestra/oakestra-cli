import json
import os
import pathlib

import oak_cli.utils.api.custom_requests as custom_requests
from oak_cli.utils.api.custom_http import HttpMethod
from oak_cli.utils.exceptions.types import OakCLIExceptionTypes

ROOT_FL_MANAGER_URL = f"http://{os.environ.get('SYSTEM_MANAGER_URL')}:5072"


def create_new_fl_service() -> None:
    sla_file_name = "flops.SLA.json"
    current_file_path = pathlib.Path(__file__).resolve()
    sla_file_path = current_file_path.parent / sla_file_name
    with open(sla_file_path, "r") as f:
        SLA = json.load(f)

    custom_requests.CustomRequest(
        custom_requests.RequestCore(
            http_method=HttpMethod.POST,
            base_url=ROOT_FL_MANAGER_URL,
            api_endpoint="/api/flops",
            data=SLA,
        ),
        custom_requests.RequestAuxiliaries(
            what_should_happen="Init new FLOps project",
            show_msg_on_success=True,
            oak_cli_exception_type=OakCLIExceptionTypes.FLOPS_PLUGIN,
        ),
    ).execute()
