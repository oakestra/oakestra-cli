from typing import Optional

import typer
from icecream import ic

from oak_cli.commands.services.auxiliary import display_single_service
from oak_cli.commands.services.get import get_all_services
from oak_cli.utils.typer_augmentations import AliasGroup
from oak_cli.utils.types import ApplicationId, Verbosity

ic.configureOutput(prefix="")
app = typer.Typer(cls=AliasGroup)


@app.command("show, s", help="Shows current services")
def show_current_services(
    verbosity: Verbosity = Verbosity.SIMPLE.value,
    app_id: Optional[ApplicationId] = typer.Option(
        None, help="ID of the parent application which services to show"
    ),
) -> None:
    current_services = get_all_services(app_id)
    for service in current_services:
        display_single_service(service=service, verbosity=verbosity)
