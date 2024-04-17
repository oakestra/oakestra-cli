import enum
import json
from typing import List

import oak_cli.utils.api.custom_requests as custom_requests
from oak_cli.utils.api.common import SYSTEM_MANAGER_URL
from oak_cli.utils.api.custom_http import HttpMethod
from oak_cli.utils.exceptions.types import OakCLIExceptionTypes
from oak_cli.utils.logging import logger
from oak_cli.utils.SLAs.common import get_SLAs_path
from oak_cli.utils.types import Application, ApplicationId


def get_application(app_id: ApplicationId) -> Application:
    return custom_requests.CustomRequest(
        custom_requests.RequestCore(
            base_url=SYSTEM_MANAGER_URL,
            api_endpoint=f"/api/application/{app_id}",
        ),
        custom_requests.RequestAuxiliaries(
            what_should_happen=f"Get application '{app_id}'",
            oak_cli_exception_type=OakCLIExceptionTypes.APP_GET,
        ),
    ).execute()


def get_applications() -> List[Application]:
    apps = custom_requests.CustomRequest(
        custom_requests.RequestCore(
            base_url=SYSTEM_MANAGER_URL,
            api_endpoint="/api/applications",
        ),
        custom_requests.RequestAuxiliaries(
            what_should_happen="Get all applications",
            oak_cli_exception_type=OakCLIExceptionTypes.APP_GET,
        ),
    ).execute()
    if not apps:
        logger.info("No applications exist yet")
    return apps


def send_sla(sla_enum: enum) -> List[Application]:
    sla_file_name = f"{sla_enum}.SLA.json"
    SLA = ""
    with open(get_SLAs_path() / sla_file_name, "r") as f:
        SLA = json.load(f)
    sla_apps = SLA["applications"]
    sla_app_names = [app["application_name"] for app in sla_apps]
    # Note: The API endpoint returns all user apps and not just the newly posted ones.
    all_user_apps = custom_requests.CustomRequest(
        custom_requests.RequestCore(
            http_method=HttpMethod.POST,
            base_url=SYSTEM_MANAGER_URL,
            api_endpoint="/api/application",
            data=SLA,
        ),
        custom_requests.RequestAuxiliaries(
            what_should_happen=f"Create new application based on '{sla_enum}'",
            show_msg_on_success=True,
            oak_cli_exception_type=OakCLIExceptionTypes.APP_CREATE,
        ),
    ).execute()

    newly_added_apps = [app for app in all_user_apps if (app["application_name"] in sla_app_names)]
    return newly_added_apps


def delete_application(app_id: ApplicationId) -> None:
    custom_requests.CustomRequest(
        custom_requests.RequestCore(
            http_method=HttpMethod.DELETE,
            base_url=SYSTEM_MANAGER_URL,
            api_endpoint=f"/api/application/{app_id}",
        ),
        custom_requests.RequestAuxiliaries(
            what_should_happen=f"Delete application '{app_id}'",
            show_msg_on_success=True,
            oak_cli_exception_type=OakCLIExceptionTypes.APP_DELETE,
        ),
    ).execute()


def delete_all_applications() -> None:
    for app in get_applications():
        delete_application(app["applicationID"])
