from typing import List

import oak_cli.utils.api.custom_requests as custom_requests
from oak_cli.utils.api.common import SYSTEM_MANAGER_URL
from oak_cli.utils.exceptions.types import OakCLIExceptionTypes
from oak_cli.utils.logging import logger
from oak_cli.utils.types import Service, ServiceId


def get_single_service(service_id: ServiceId) -> Service:
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


def get_all_services(app_id: ServiceId = None) -> List[Service]:
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

    if not services:
        logger.info("No applications exist yet")
    return services
