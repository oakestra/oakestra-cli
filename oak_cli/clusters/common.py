import oak_cli.utils.api.custom_requests as custom_requests
from oak_cli.utils.api.common import get_system_manager_url
from oak_cli.utils.exceptions.main import OakCLIException
from oak_cli.utils.exceptions.types import OakCLIExceptionTypes
from oak_cli.utils.types import Cluster


def get_clusters(all: bool) -> Cluster:  # type: ignore
    try:
        return custom_requests.CustomRequest(
            custom_requests.RequestCore(
                base_url=get_system_manager_url(),
                api_endpoint=f"/api/clusters/{'' if all else 'active'}",
            ),
            custom_requests.RequestAuxiliaries(
                what_should_happen=f"Get {'' if all else 'active'} clusters",
                oak_cli_exception_type=OakCLIExceptionTypes.APP_GET,
            ),
        ).execute()
    except OakCLIException as e:
        e.handle_exception(
            oak_cli_exception_type=OakCLIExceptionTypes.APP_GET,
            special_message=f"Cluster information could not be retrieved. {e}",
        )
