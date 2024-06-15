from typing import List

import rich

from oak_cli.services.common import get_all_services, get_single_service
from oak_cli.utils.styling import (
    OAK_BLUE,
    OAK_GREEN,
    OAK_WHITE,
    add_column,
    add_plain_columns,
    create_table,
)
from oak_cli.utils.types import ApplicationId, ServiceId, Verbosity


def add_icon_to_status(status: str) -> str:
    STATUS_ICON_MAP = {
        "COMPLETED": "✅",
        "RUNNING": "🟢",
        "ACTIVE": "🔷",
        "CLUSTER_SCHEDULED": "🟣",
        "NODE_SCHEDULED": "🔵",
        "NoActiveClusterWithCapacity": "❌",
    }
    return f"{status} {STATUS_ICON_MAP.get(status, '❓')}"


def show_instances(instances: List[dict]) -> str:
    instance_status_info = []
    for i in instances:
        status = i.get("status")
        info = (
            f"{i['instance_number']}:{add_icon_to_status(status) if status else 'No Status Yet ⚪'}"
        )
        instance_status_info.append(info)

    resulting_string = f"({len(instances)})"
    if len(instance_status_info) > 0:
        resulting_string += f" - {instance_status_info}"
    return resulting_string


def generate_current_services_table(
    app_id: ApplicationId,
    verbosity: Verbosity,
    live: bool = False,
) -> rich.table.Table:
    current_services = get_all_services(app_id)
    caption = "Current Services"
    if app_id:
        app_name = current_services[0]["app_name"]
        caption += f" of app: '{app_name} - {app_id}'"
    table = create_table(caption=caption, verbosity=verbosity, live=live)
    add_column(table, column_name="Service Name", style=OAK_GREEN)
    add_column(table, column_name="Service ID")
    add_column(table, column_name="Status", style=OAK_WHITE)
    add_column(table, column_name="Instances", style=OAK_WHITE)
    if not app_id:
        add_column(table, column_name="App Name", style=OAK_BLUE)
        add_column(table, column_name="App ID")
    if verbosity == Verbosity.DETAILED:
        add_plain_columns(table, column_names=["Image", "Command"])

    for service in current_services:
        special_row_elements = []
        if verbosity == Verbosity.DETAILED:
            special_row_elements += [
                service["image"],
                " ".join(service["cmd"]) if service["cmd"] else "-",
            ]

        service_status = service.get("status")
        row_elements = [
            service["microservice_name"],
            service["microserviceID"],
            add_icon_to_status(service_status) if service_status else "-",
            show_instances(instances=service["instance_list"]),
        ]
        if not app_id:
            row_elements += [
                service["app_name"],
                service["applicationID"],
            ]
        row_elements += special_row_elements
        table.add_row(*row_elements)

    return table


def generate_service_inspection_table(
    service_id: ServiceId,
    live: bool = False,
) -> rich.table.Table:
    # NOTE: We use a grid instead of a table, because the live-display
    # can only support a single object not multiple at once.
    service = get_single_service(service_id=service_id)
    instances = service["instance_list"]
    instance_status = service.get("status")
    title = " | ".join(
        (
            f"name: {service['microservice_name']}",
            add_icon_to_status(instance_status) if instance_status else "-",
            f"app name: {service['app_name']}",
            f"app ID: {service['applicationID']}",
        )
    )
    caption = " | ".join(
        (
            f"image: {service['image']}",
            f"cmd: {' '.join(service['cmd']) if service['cmd'] else '-'}",
        )
    )
    table = create_table(title=title, caption=caption, live=live)
    service = get_single_service(service_id=service_id)
    instances = service["instance_list"]

    add_column(table, "#", style=OAK_BLUE)
    add_column(table, "Status", style=OAK_WHITE)
    add_column(table, "Logs", style=OAK_GREEN)
    for instance in instances:
        instance_status = instance.get("status")
        row_elements = [
            str(instance.get("instance_number")),
            add_icon_to_status(instance_status) if instance_status else "-",
            instance.get("logs"),
        ]
        table.add_row(*row_elements)
    return table
