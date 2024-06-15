from typing import Optional

import typer
from icecream import ic
from typing_extensions import Annotated

from oak_cli.commands.services.auxiliary import add_icon_to_status, show_instances
from oak_cli.commands.services.get import get_all_services
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
from oak_cli.utils.types import ApplicationId, Verbosity

ic.configureOutput(prefix="")
app = typer.Typer(cls=AliasGroup)


@app.command("show, s", help="Shows current services")
def show_current_services(
    verbosity: Annotated[Optional[Verbosity], typer.Option("-v")] = Verbosity.SIMPLE.value,
    app_id: Optional[ApplicationId] = typer.Option(
        None, help="ID of the parent application which services to show"
    ),
) -> None:
    current_services = get_all_services(app_id)
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
