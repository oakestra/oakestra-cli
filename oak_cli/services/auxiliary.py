from typing import List

import rich

from oak_cli.services.common import get_all_services
from oak_cli.utils.styling import (
    LIVE_VIEW_PREFIX,
    OAK_BLUE,
    OAK_GREEN,
    OAK_WHITE,
    add_column,
    add_plain_columns,
    create_table,
)
from oak_cli.utils.types import ApplicationId, Verbosity


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
