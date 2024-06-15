from typing import List

import oak_cli.utils.api.custom_requests as custom_requests
from oak_cli.utils.api.common import SYSTEM_MANAGER_URL
from oak_cli.utils.api.custom_http import HttpMethod
from oak_cli.utils.exceptions.types import OakCLIExceptionTypes
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
    return apps


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
