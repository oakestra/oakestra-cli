import json
import os

import oak_cli.utils.api.custom_requests as custom_requests
from oak_cli.commands.plugins.flops.SLAs.common import FLOpsSLAs, get_FLOps_SLAs_path
from oak_cli.utils.api.custom_http import HttpMethod
from oak_cli.utils.exceptions.types import OakCLIExceptionTypes

ROOT_FL_MANAGER_URL = f"http://{os.environ.get('SYSTEM_MANAGER_URL')}:5072"


def create_new_flops_project(sla: FLOpsSLAs) -> None:
    with open(get_FLOps_SLAs_path() / f"{sla.value}.SLA.json", "r") as f:
        SLA = json.load(f)

    custom_requests.CustomRequest(
        custom_requests.RequestCore(
            http_method=HttpMethod.POST,
            base_url=ROOT_FL_MANAGER_URL,
            api_endpoint="/api/flops",
            data=SLA,
        ),
        custom_requests.RequestAuxiliaries(
            what_should_happen=f"Init new FLOps project for SLA '{sla}'",
            show_msg_on_success=True,
            oak_cli_exception_type=OakCLIExceptionTypes.FLOPS_PLUGIN,
        ),
    ).execute()
