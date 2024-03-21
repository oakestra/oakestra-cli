from typing import List

from oak_cli.utils.api.common import SYSTEM_MANAGER_URL, HttpMethod
from oak_cli.utils.api.main import handle_request
from oak_cli.utils.types import Service, ServiceId


def get_single_service(service_id: ServiceId) -> Service:
    service = handle_request(
        base_url=SYSTEM_MANAGER_URL,
        http_method=HttpMethod.GET,
        api_endpoint=f"/api/service/{service_id}",
        what_should_happen=f"Get single service '{service_id}'",
    )
    return service


def get_all_services(app_id: ServiceId = None) -> List[Service]:
    what_should_happen = "Get all services"
    if app_id:
        what_should_happen += f" of app '{app_id}'"

    services = handle_request(
        base_url=SYSTEM_MANAGER_URL,
        http_method=HttpMethod.GET,
        api_endpoint=f"/api/services/{app_id or ''}",
        what_should_happen=what_should_happen,
    )
    return services
