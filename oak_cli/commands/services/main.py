from typing import Optional

import rich
import typer
from icecream import ic
from typing_extensions import Annotated

from oak_cli.commands.services.auxiliary import add_icon_to_status, show_instances
from oak_cli.commands.services.get import get_all_services
from oak_cli.utils.styling import OAK_BLUE, OAK_GREEN, add_column, create_table, print_table
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
    add_column(table, column_name="Service Name", style=OAK_GREEN, justify="left")
    add_column(table, column_name="Service ID")
    add_column(table, column_name="Status", style="white")
    add_column(table, column_name="Instances", style="white")
    add_column(table, column_name="App Name", style=OAK_BLUE)
    add_column(table, column_name="App ID")
    if verbosity == Verbosity.DETAILED:
        # FUTURE WORK / TODO: Think what properties might be interesting.
        # Might need to simplify the SIMPLE case because the table already is quite large.
        pass

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
                # FUTURE WORK / TODO: Think what properties might be interesting.
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
