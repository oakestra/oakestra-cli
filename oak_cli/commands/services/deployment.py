import oak_cli.utils.api.custom_requests as custom_requests
from oak_cli.commands.services.get import get_single_service
from oak_cli.utils.api.common import SYSTEM_MANAGER_URL
from oak_cli.utils.api.custom_http import HttpMethod
from oak_cli.utils.exceptions.types import OakCLIExceptionTypes
from oak_cli.utils.types import Id, ServiceId


def deploy_new_instance(service_id: ServiceId) -> None:
    custom_requests.CustomRequest(
        custom_requests.RequestCore(
            http_method=HttpMethod.POST,
            base_url=SYSTEM_MANAGER_URL,
            api_endpoint=f"/api/service/{service_id}/instance",
        ),
        custom_requests.RequestAuxiliaries(
            what_should_happen=f"Deploy a new instance for the service '{service_id}'",
            show_msg_on_success=True,
            oak_cli_exception_type=OakCLIExceptionTypes.SERVICE_DEPLOYMENT,
        ),
    ).execute()


def undeploy_instance(service_id: ServiceId, instance_id: Id = None) -> None:
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


def undeploy_all_instances_of_service(service_id: ServiceId) -> None:
    service = get_single_service(service_id)
    for instance in service["instance_list"]:
        undeploy_instance(service_id, instance["instance_number"])
