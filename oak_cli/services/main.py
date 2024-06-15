from typing import Optional

import typer
from icecream import ic
from typing_extensions import Annotated

import oak_cli.utils.api.custom_requests as custom_requests
from oak_cli.services.auxiliary import add_icon_to_status, show_instances
from oak_cli.services.common import get_all_services, get_single_service, undeploy_instance
from oak_cli.utils.api.common import SYSTEM_MANAGER_URL
from oak_cli.utils.api.custom_http import HttpMethod
from oak_cli.utils.exceptions.types import OakCLIExceptionTypes
from oak_cli.utils.styling import (
    OAK_BLUE,
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


@app.command("show, s", help="Shows current services.")
def show_current_services(
    verbosity: Annotated[Optional[Verbosity], typer.Option("-v")] = Verbosity.SIMPLE.value,
    app_id: Optional[ApplicationId] = typer.Option(
        None, help="ID of the parent application which services to show"
    ),
) -> None:
    current_services = get_all_services(app_id)
    if not current_services:
        return

    table = create_table(caption="Current Services", verbosity=verbosity)
    add_column(table, column_name="Service Name", style=OAK_GREEN)
    add_column(table, column_name="Service ID")
    add_column(table, column_name="Status", style=OAK_WHITE)
    add_column(table, column_name="Instances", style=OAK_WHITE)
    add_column(table, column_name="App Name", style=OAK_BLUE)
    add_column(table, column_name="App ID")
    if verbosity == Verbosity.DETAILED:
        add_plain_columns(table, column_names=["Image", "Command"])

    for i, service in enumerate(current_services):
        special_row_elements = []
        match verbosity:
            case Verbosity.EXHAUSTIVE:
                # NOTE: Hide information that is too verbose.
                for instance in service["instance_list"]:
                    instance["cpu_history"] = "..."
                    instance["memory_history"] = "..."
                    instance["logs"] = "..."
                ic(i, service)
                continue
            case Verbosity.DETAILED:
                special_row_elements += [
                    service["image"],
                    " ".join(service["cmd"]) if service["cmd"] else "-",
                ]
                pass

        row_elements = [
            service["microservice_name"],
            service["microserviceID"],
            add_icon_to_status(service["status"]),
            show_instances(instances=service["instance_list"]),
            service["app_name"],
            service["applicationID"],
        ] + special_row_elements
        table.add_row(*row_elements)

    if verbosity == Verbosity.EXHAUSTIVE:
        return

    print_table(table)


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
