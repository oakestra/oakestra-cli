import json
import os
import pathlib

from oak_cli.utils.api.common import HttpMethod
from oak_cli.utils.api.main import handle_request

ROOT_FL_MANAGER_URL = f"http://{os.environ.get('SYSTEM_MANAGER_URL')}:5072"


def create_new_fl_service() -> None:
    sla_file_name = "flops.SLA.json"
    current_file_path = pathlib.Path(__file__).resolve()
    sla_file_path = current_file_path.parent / sla_file_name
    with open(sla_file_path, "r") as f:
        SLA = json.load(f)

    handle_request(
        base_url=ROOT_FL_MANAGER_URL,
        http_method=HttpMethod.POST,
        data=SLA,
        api_endpoint="/api/flops",
        what_should_happen="Init new FLOps processes",
        show_msg_on_success=True,
    )
