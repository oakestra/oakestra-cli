from oak_cli.commands.services.get import get_all_services
from oak_cli.utils.logging import logger
from oak_cli.utils.types import ApplicationId, Service


def _log_aux_service(key: str, value: str, service: Service) -> None:
    value = service.get(value, None)
    if value is not None:
        _log_aux(key, value)


def _log_aux(key: str, value: str) -> None:
    logger.debug(f"   {key}: '{value}'")


def verbose_log_aux(section_name: str) -> None:
    logger.info(f"   - {section_name} -")


def display_single_service(service: Service, verbose: bool = False) -> None:
    verbose_log_aux("microservice")
    _log_aux_service("id", "microserviceID", service)
    _log_aux_service("microservice name" if verbose else "name", "microservice_name", service)
    _log_aux_service("microservice ns" if verbose else "ns", "microservice_namespace", service)
    _log_aux("parent app", f"{service['app_name']}: {service['applicationID']}")

    if verbose:
        verbose_log_aux("service")
        _log_aux_service("service name", "service_name", service)

    verbose_log_aux("resources")
    _log_aux_service("memory", "memory", service)
    _log_aux_service("vcpus", "vcpus", service)
    if verbose:
        _log_aux_service("storage", "storage", service)
        _log_aux_service("vgpus", "vgpus", service)

    verbose_log_aux("container")
    _log_aux_service("image", "image", service)
    if verbose:
        _log_aux_service("code", "code", service)

    verbose_log_aux("networking")
    _log_aux_service("port", "port", service)
    if verbose:
        _log_aux_service("bandwidth in", "bandwidth_in", service)
        _log_aux_service("bandwidth out", "bandwidth_out", service)

    verbose_log_aux("instances")
    instances = service["instance_list"]
    num_instances = len(instances)
    _log_aux("instances", num_instances)
    if verbose and num_instances > 0:
        for i, instance in enumerate(instances):
            logger.info(f"   Instance '{i}':")
            _log_aux("  instance_number", instance["instance_number"])
            _log_aux("  status", instance["status"])
            _log_aux("  publicip", instance["publicip"])
            _log_aux("  cpu", instance["cpu"])


def display_all_current_services(
    verbose: bool = False,
    app_id: ApplicationId = None,
) -> None:
    all_current_services = get_all_services(app_id)

    logger.info(f"All current services: '{len(all_current_services)}'")
    for i, service in enumerate(all_current_services):
        logger.warning(f" Service '{i}':")
        display_single_service(service, verbose)
