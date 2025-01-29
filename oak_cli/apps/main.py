import json
from typing import List, Optional

import typer
from icecream import ic
from typing_extensions import Annotated

import oak_cli.utils.api.custom_requests as custom_requests
from oak_cli.apps.auxiliary import generate_current_application_table
from oak_cli.apps.common import delete_application, get_applications
from oak_cli.apps.prepared_SLAs.main import get_sla_file_path
from oak_cli.services.main import deploy_new_instance
from oak_cli.utils.api.common import get_system_manager_url
from oak_cli.utils.api.custom_http import HttpMethod
from oak_cli.utils.common import print_sla
from oak_cli.utils.exceptions.types import OakCLIExceptionTypes
from oak_cli.utils.logging import logger
from oak_cli.utils.styling import display_table
from oak_cli.utils.typer_augmentations import AliasGroup
from oak_cli.utils.types import (
    LIVE_VIEW_FLAG_TYPE,
    VERBOSITY_FLAG_TYPE,
    Application,
    ApplicationId,
    Verbosity,
)

app = typer.Typer(cls=AliasGroup)


@app.command("show, s", help="Show current applications")
def show_current_applications(
    live: LIVE_VIEW_FLAG_TYPE = False,
    verbosity: VERBOSITY_FLAG_TYPE = Verbosity.SIMPLE.value,  # type: ignore
) -> None:
    current_applications = get_applications()
    if not live and not current_applications:
        logger.info("No applications exist yet")
        return

    if verbosity == Verbosity.EXHAUSTIVE:
        for i, application in enumerate(current_applications):
            ic(i, application)
        return

    display_table(
        live,
        table_generator=lambda: generate_current_application_table(
            verbosity=Verbosity(verbosity),
            live=live,
        ),
    )


@app.command("create, c", help="Create one or multiple apps based on an SLA")
def create_applications(
    sla_file_name: Optional[str] = typer.Option(
        default="",
        help="If not provided an interactive selection of available SLAs is shown",
    ),
    deploy: Annotated[
        bool, typer.Option("-d", help="Deploy the application service(s) after creating the app")
    ] = False,
) -> List[Application]:
    sla_file_path = get_sla_file_path(sla_file_name)
    with open(sla_file_path, "r") as f:
        SLA = json.load(f)
    sla_apps = SLA["applications"]
    sla_app_names = [app["application_name"] for app in sla_apps]
    # Note: The API endpoint returns all user apps and not just the newly posted ones.
    all_user_apps = custom_requests.CustomRequest(
        custom_requests.RequestCore(
            http_method=HttpMethod.POST,
            base_url=get_system_manager_url(),
            api_endpoint="/api/application",
            data=SLA,
        ),
        custom_requests.RequestAuxiliaries(
            what_should_happen=f"Create new application based on '{sla_file_path}'",
            show_msg_on_success=True,
            oak_cli_exception_type=OakCLIExceptionTypes.APP_CREATE,
        ),
    ).execute()

    newly_added_apps = [app for app in all_user_apps if (app["application_name"] in sla_app_names)]

    if deploy:
        for app in newly_added_apps:
            for service_id in app["microservices"]:
                deploy_new_instance(service_id=service_id)

    return newly_added_apps


@app.command("delete, d", help="Delete all applications or only the specified one")
def delete_applications(
    app_id: Optional[ApplicationId] = typer.Argument(None, help="ID of the application to delete"),
    skip_confirmation: bool = typer.Option(False, "-y", help="Skip confirmation prompt"),
) -> None:
    if app_id:
        delete_application(app_id)
        return

    apps = get_applications()
    if len(apps) == 0:
        logger.info("No applications exist yet")
        return

    if not skip_confirmation:
        what_to_delete_txt = (
            f"all '{len(apps)}' applications" if len(apps) > 1 else "the active application"
        )
        typer.confirm(
            f"Are you certain to delete {what_to_delete_txt}",
            abort=True,
        )
    for app in apps:
        delete_application(app["applicationID"])


@app.command("sla", help="Display available SLAs")
def display_app_sla(
    sla_file_name: Optional[str] = typer.Option(
        "",
        help="If no SLA is initially provided an interactive selection of available SLAs is shown",
    ),
) -> None:
    sla_file_path = get_sla_file_path(sla_file_name)
    print_sla(sla_file_path)
