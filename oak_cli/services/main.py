import time
from typing import Optional

import typer
from icecream import ic
from rich.live import Live
from typing_extensions import Annotated

import oak_cli.utils.api.custom_requests as custom_requests
from oak_cli.services.auxiliary import add_icon_to_status, generate_current_services_table
from oak_cli.services.common import get_all_services, get_single_service, undeploy_instance
from oak_cli.utils.api.common import SYSTEM_MANAGER_URL
from oak_cli.utils.api.custom_http import HttpMethod
from oak_cli.utils.exceptions.types import OakCLIExceptionTypes
from oak_cli.utils.logging import logger
from oak_cli.utils.styling import (
    LIVE_HELP_TEXT,
    LIVE_REFRESH_RATE,
    OAK_GREEN,
    OAK_WHITE,
    add_column,
    add_plain_columns,
    create_table,
    print_table,
)
from oak_cli.utils.typer_augmentations import AliasGroup
from oak_cli.utils.types import ApplicationId, Id, ServiceId, Verbosity

ic.configureOutput(prefix="")
app = typer.Typer(cls=AliasGroup)


@app.command("inspect, i", help="Inspect the specified service.")
def inspect_service(service_id: ServiceId) -> None:
    service = get_single_service(service_id=service_id)
    instances = service["instance_list"]
    caption = "" if instances else "No instances deployed"
    service_table = create_table(caption=caption)
    add_column(service_table, column_name="Service Name", style=OAK_GREEN)
    add_column(service_table, column_name="Service Status", style=OAK_WHITE)
    add_plain_columns(service_table, column_names=["App Name", "App ID", "Image", "Command"])
    service_status = service.get("status")
    service_table.add_row(
        service["microservice_name"],
        add_icon_to_status(service_status) if service_status else "-",
        service["app_name"],
        service["applicationID"],
        service["image"],
        " ".join(service["cmd"]) if service["cmd"] else "-",
    )
    print_table(service_table)
    if not instances:
        return

    instances_table = create_table(title="Instances")
    add_column(instances_table, "#", style=OAK_GREEN)
    add_column(instances_table, "Logs")
    for instance in instances:
        row_elements = [
            str(instance.get("instance_number")),
            instance.get("logs"),
        ]
        instances_table.add_row(*row_elements)
    print_table(instances_table)


@app.command("show, s", help="Shows current services.")
def show_current_services(
    app_id: Annotated[
        Optional[ApplicationId],
        typer.Argument(help="ID of the parent application which services to show"),
    ] = None,
    live: Annotated[Optional[bool], typer.Option("-l", help=LIVE_HELP_TEXT)] = False,
    verbosity: Annotated[Optional[Verbosity], typer.Option("-v")] = Verbosity.SIMPLE.value,
) -> None:
    current_services = get_all_services(app_id)

    if not live and not current_services:
        logger.info("No services exist yet")
        return

    if verbosity == Verbosity.EXHAUSTIVE:
        for i, service in enumerate(current_services):
            # NOTE: Hide information that is too verbose.
            HIDDEN_TEXT = "(hidden by CLI)"
            for instance in service["instance_list"]:
                instance["cpu_history"] = HIDDEN_TEXT
                instance["memory_history"] = HIDDEN_TEXT
                instance["logs"] = HIDDEN_TEXT
            ic(i, service)
            continue
        return

    if not live:
        print_table(table=generate_current_services_table(app_id, verbosity))
        return

    with Live(
        generate_current_services_table(app_id, verbosity),
        auto_refresh=False,
    ) as live:
        while True:
            time.sleep(LIVE_REFRESH_RATE)
            live.update(generate_current_services_table(app_id, verbosity), refresh=True)


@app.command("deploy, d", help="Deploy a new service instance.")
def deploy_new_instance(service_id: ServiceId) -> None:
    custom_requests.CustomRequest(
        custom_requests.RequestCore(
            http_method=HttpMethod.POST,
            base_url=SYSTEM_MANAGER_URL,
            api_endpoint=f"/api/service/{service_id}/instance",
        ),
        custom_requests.RequestAuxiliaries(
            what_should_happen=f"Deploy a new instance for the service '{service_id}'.",
            show_msg_on_success=True,
            oak_cli_exception_type=OakCLIExceptionTypes.SERVICE_DEPLOYMENT,
        ),
    ).execute()


UNDEPLOY_HELP = """
Undeploy all services or only the specified ones.
Without any optional flags undeploys all services.
"""

INSTANCE_ID_HELP = """
Requires the 'service_id' to be provided.
Undeploys only the single instance of the specified service.
"""


@app.command("undeploy, u", help=UNDEPLOY_HELP)
def undeploy_instances(
    service_id: Annotated[
        ServiceId,
        typer.Option(help="If provided will only undeploy all instances of that service."),
    ] = None,
    instance_id: Annotated[Id, typer.Option(help=INSTANCE_ID_HELP)] = None,
) -> None:
    def undeploy_service_instances(service: dict) -> None:
        for instance in service["instance_list"]:
            undeploy_instance(
                service_id=service["microserviceID"],
                instance_id=instance["instance_number"],
            )

    if service_id:
        service = get_single_service(service_id)
        if instance_id:
            undeploy_instance(service_id=service_id, instance_id=instance_id)
            return
        undeploy_service_instances(service)
        return

    for service in get_all_services():
        undeploy_service_instances(service=service)
