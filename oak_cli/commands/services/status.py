from icecream import ic

from oak_cli.commands.services.get import get_all_services
from oak_cli.utils.types import ApplicationId, Service

ic.configureOutput(prefix="")


def display_single_service(service: Service, verbose: bool = False) -> None:
    if verbose:
        for instance in service["instance_list"]:
            instance["cpu_history"] = "..."
            instance["memory_history"] = "..."
            instance["logs"] = "..."
    else:
        mask = [
            "addresses",
            "app_name",
            "app_ns",
            "applicationID",
            "service_name",
            "service_ns",
            "service_ns",
            "one_shot",
            "microserviceID",
            "cmd",
            "code",
            "image",
        ]
        service = {key: service[key] for key in mask if key in service}
    ic(service)


def display_all_current_services(
    verbose: bool = False,
    app_id: ApplicationId = None,
) -> None:
    all_current_services = get_all_services(app_id)
    for i, service in enumerate(all_current_services):
        ic(i)
        display_single_service(service, verbose)
