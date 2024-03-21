import enum
import json
from typing import List

from oak_cli.utils.api.common import SYSTEM_MANAGER_URL, HttpMethod
from oak_cli.utils.api.main import handle_request
from oak_cli.utils.SLAs.common import get_SLAs_path
from oak_cli.utils.types import Application, ApplicationId


def get_application(app_id: ApplicationId) -> Application:
    app = handle_request(
        base_url=SYSTEM_MANAGER_URL,
        http_method=HttpMethod.GET,
        api_endpoint=f"/api/application/{app_id}",
        what_should_happen=f"Get application '{app_id}'",
    )
    return app


def get_applications() -> List[Application]:
    apps = handle_request(
        base_url=SYSTEM_MANAGER_URL,
        http_method=HttpMethod.GET,
        api_endpoint="/api/applications",
        what_should_happen="Get all applications",
    )
    return apps


def send_sla(sla_enum: enum) -> List[Application]:
    sla_file_name = f"{sla_enum}.SLA.json"
    SLA = ""
    with open(get_SLAs_path() / sla_file_name, "r") as f:
        SLA = json.load(f)
    sla_apps = SLA["applications"]
    sla_app_names = [app["application_name"] for app in sla_apps]
    # Note: The API endpoint returns all user apps and not just the newly posted ones.
    all_user_apps = handle_request(
        base_url=SYSTEM_MANAGER_URL,
        http_method=HttpMethod.POST,
        data=SLA,
        api_endpoint="/api/application",
        what_should_happen=f"Create new application based on '{sla_enum}'",
        show_msg_on_success=True,
    )
    newly_added_apps = [app for app in all_user_apps if (app["application_name"] in sla_app_names)]
    return newly_added_apps


def delete_application(app_id: ApplicationId) -> None:
    handle_request(
        base_url=SYSTEM_MANAGER_URL,
        http_method=HttpMethod.DELETE,
        api_endpoint=f"/api/application/{app_id}",
        what_should_happen=f"Delete application '{app_id}'",
        show_msg_on_success=True,
    )


def delete_all_applications() -> None:
    for app in get_applications():
        delete_application(app["applicationID"])
