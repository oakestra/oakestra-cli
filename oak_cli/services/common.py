from typing import List, Optional

import oak_cli.utils.api.custom_requests as custom_requests
from oak_cli.utils.api.common import SYSTEM_MANAGER_URL
from oak_cli.utils.api.custom_http import HttpMethod
from oak_cli.utils.exceptions.main import OakCLIException
from oak_cli.utils.exceptions.types import OakCLIExceptionTypes
from oak_cli.utils.types import ApplicationId, Id, Service, ServiceId


def get_single_service(service_id: ServiceId) -> Service:
    try:
        return custom_requests.CustomRequest(
            custom_requests.RequestCore(
                base_url=SYSTEM_MANAGER_URL,
                api_endpoint=f"/api/service/{service_id}",
            ),
            custom_requests.RequestAuxiliaries(
                what_should_happen=f"Get single service '{service_id}'",
                oak_cli_exception_type=OakCLIExceptionTypes.SERVICE_GET,
            ),
        ).execute()
    except OakCLIException as e:
        e.handle_exception(
            oak_cli_execption_type=OakCLIExceptionTypes.SERVICE_GET,
            special_message=f"Service '{service_id}' not found.",
        )


def get_all_services(app_id: ApplicationId = None) -> List[Service]:
    what_should_happen = "Get all services"
    if app_id:
        what_should_happen += f" of app '{app_id}'"
    services = custom_requests.CustomRequest(
        custom_requests.RequestCore(
            base_url=SYSTEM_MANAGER_URL,
            api_endpoint=f"/api/services/{app_id or ''}",
        ),
        custom_requests.RequestAuxiliaries(
            what_should_happen=what_should_happen,
            oak_cli_exception_type=OakCLIExceptionTypes.SERVICE_GET,
        ),
    ).execute()
    # NOTE: From my understanding the OAK endpoint does not work properly.
    # It seems to NOT only return services of the provided app but more.
    if app_id:
        services = [service for service in services if service["applicationID"] == app_id]
    return services


def undeploy_instance(service_id: ServiceId, instance_id: Optional[Id] = None) -> None:
    custom_requests.CustomRequest(
        custom_requests.RequestCore(
            http_method=HttpMethod.DELETE,
            base_url=SYSTEM_MANAGER_URL,
            api_endpoint=f"/api/service/{service_id}/instance/{instance_id or 0}",
        ),
        custom_requests.RequestAuxiliaries(
            what_should_happen=f"Undeploy instance '{instance_id or 0}' for service '{service_id}'",
            show_msg_on_success=True,
            oak_cli_exception_type=OakCLIExceptionTypes.SERVICE_UNDEPLOYMENT,
        ),
    ).execute()
