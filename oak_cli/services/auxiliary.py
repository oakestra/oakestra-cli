from typing import List

import rich
from oakestra_utils.types.statuses import (
    DeploymentStatus,
    NegativeSchedulingStatus,
    PositiveSchedulingStatus,
    convert_to_status,
)

from oak_cli.services.common import get_all_services, get_single_service
from oak_cli.utils.styling import (
    OAK_BLUE,
    OAK_GREEN,
    OAK_WHITE,
    add_column,
    add_plain_columns,
    add_row_to_table,
    create_table,
)
from oak_cli.utils.types import ApplicationId, ServiceId, Verbosity


def add_icon_to_status(status_name: str) -> str:
    if not status_name:
        return "-"

    status = convert_to_status(status_name)
    STATUS_ICON_MAP = {
        PositiveSchedulingStatus.REQUESTED: "🟡",
        PositiveSchedulingStatus.CLUSTER_SCHEDULED: "🟣",
        PositiveSchedulingStatus.NODE_SCHEDULED: "🔵",
        DeploymentStatus.CREATING: "🔨",
        DeploymentStatus.CREATED: "🛠️",
        DeploymentStatus.RUNNING: "🟢",
        DeploymentStatus.FAILED: "❌",
        DeploymentStatus.DEAD: "💀",
        DeploymentStatus.COMPLETED: "✅",
        DeploymentStatus.UNDEPLOYED: "⚫",
    }
    if isinstance(status, NegativeSchedulingStatus):
        status_icon = "❌"
    else:
        status_icon = STATUS_ICON_MAP.get(status, "❓")

    return f"{status} {status_icon}"


def create_instances_sub_table(
    instances: List[dict], verbosity: Verbosity = Verbosity.SIMPLE
) -> rich.table.Table:
    table = create_table(
        box=rich.box.SIMPLE,
        pad_edge=False,
        padding=0,
        show_header=(verbosity == Verbosity.DETAILED),
    )
    add_column(table, column_name="#")
    add_column(table, column_name="status", style=OAK_WHITE)
    if verbosity == Verbosity.DETAILED:
        add_column(table, column_name="public IP")
        add_column(table, column_name="cluster ID")

    for i in instances:
        status = i.get("status")
        row_items = [
            str(i["instance_number"]),
            add_icon_to_status(status),
        ]
        if verbosity == Verbosity.DETAILED:
            row_items += [i.get("publicip"), i.get("cluster_id")]
        add_row_to_table(table=table, row_items=row_items)
    return table


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
    add_column(
        table,
        column_name="Service ID",
        no_wrap=(verbosity == Verbosity.SIMPLE),
    )
    if verbosity == Verbosity.DETAILED:
        add_column(table, column_name="Status", style=OAK_WHITE)
    add_column(table, column_name="Instances", style=OAK_WHITE, no_wrap=True)
    if not app_id:
        add_column(table, column_name="App Name", style=OAK_BLUE)
        add_column(table, column_name="App ID")
    if verbosity == Verbosity.DETAILED:
        add_plain_columns(table, column_names=["Image", "Command"])

    for service in current_services:
        special_row_items = []
        if verbosity == Verbosity.DETAILED:
            special_row_items += [
                service["image"],
                " ".join(service["cmd"]) if service["cmd"] else "-",
            ]

        service_status = service.get("status")

        instances = service["instance_list"]
        instance_info = "-"
        if len(instances) > 0:
            instance_info = create_instances_sub_table(instances=instances, verbosity=verbosity)

        row_items = [service["microservice_name"], service["microserviceID"]]
        if verbosity == Verbosity.DETAILED:
            row_items.append(add_icon_to_status(service_status))
        row_items.append(instance_info)
        if not app_id:
            row_items += [
                service["app_name"],
                service["applicationID"],
            ]
        row_items += special_row_items
        add_row_to_table(table=table, row_items=row_items)

    return table


def generate_service_inspection_table(
    service_id: ServiceId,
    live: bool = False,
) -> rich.table.Table:
    # NOTE: Initially the instance number and instance status had their own status.
    # This lead to a lot of unused screen space.
    # To maximize the available screen space all contents are placed into a single column.
    # This might not be a great solution but it works. POTENTIAL FUTURE WORK
    service = get_single_service(service_id=service_id)
    instances = service["instance_list"]
    instance_status = service.get("status")
    title = " | ".join(
        (
            f"name: {service['microservice_name']}",
            add_icon_to_status(instance_status),
            f"app name: {service['app_name']}",
            f"app ID: {service['applicationID']}",
        )
    )
    caption = " | ".join(
        (
            f"image: {service['image']}",
            f"cmd: {' '.join(service.get('cmd')) if service.get('cmd') else '-'}",
        )
    )
    table = create_table(caption=caption, live=live)
    service = get_single_service(service_id=service_id)
    instances = service["instance_list"]
    add_column(table, title, style=OAK_GREEN)
    for instance in instances:
        instance_status = instance.get("status")
        general_instance_info = f"[{OAK_BLUE}]" + " | ".join(
            (
                str(instance.get("instance_number")),
                add_icon_to_status(instance_status),
                f"public IP: {instance.get('publicip')}",
                f"cluster ID: {instance.get('cluster_id')}",
                "Logs :",
            )
        )
        add_row_to_table(table=table, row_items=general_instance_info)
        add_row_to_table(table=table, row_items=instance.get("logs"))
    return table
