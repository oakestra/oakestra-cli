from oak_cli.commands.services.get import get_single_service
from oak_cli.utils.api.common import SYSTEM_MANAGER_URL, HttpMethod
from oak_cli.utils.api.main import handle_request
from oak_cli.utils.types import Id, ServiceId


def deploy_new_instance(service_id: ServiceId) -> None:
    handle_request(
        base_url=SYSTEM_MANAGER_URL,
        http_method=HttpMethod.POST,
        api_endpoint=f"/api/service/{service_id}/instance",
        what_should_happen=f"Deploy a new instance for the service '{service_id}'",
        show_msg_on_success=True,
    )


def undeploy_instance(service_id: ServiceId, instance_id: Id = None) -> None:
    handle_request(
        base_url=SYSTEM_MANAGER_URL,
        http_method=HttpMethod.DELETE,
        api_endpoint=f"/api/service/{service_id}/instance/{instance_id or 0}",
        what_should_happen=f"Undeploy instance '{instance_id or 0}' for the service '{service_id}'",
        show_msg_on_success=True,
    )


def undeploy_all_instances_of_service(service_id: ServiceId) -> None:
    service = get_single_service(service_id)
    for instance in service["instance_list"]:
        undeploy_instance(service_id, instance["instance_number"])
