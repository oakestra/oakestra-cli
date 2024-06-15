import json
from typing import List, Optional

import typer
from icecream import ic
from typing_extensions import Annotated

import oak_cli.utils.api.custom_requests as custom_requests
from oak_cli.apps.auxiliary import generate_current_application_table
from oak_cli.apps.common import delete_application, get_applications
from oak_cli.apps.SLAs.common import AppSLAs, get_SLAs_path
from oak_cli.services.main import deploy_new_instance
from oak_cli.utils.api.common import SYSTEM_MANAGER_URL
from oak_cli.utils.api.custom_http import HttpMethod
from oak_cli.utils.exceptions.types import OakCLIExceptionTypes
from oak_cli.utils.logging import logger
from oak_cli.utils.styling import LIVE_HELP_TEXT, display_table
from oak_cli.utils.typer_augmentations import AliasGroup
from oak_cli.utils.types import Application, ApplicationId, Verbosity

app = typer.Typer(cls=AliasGroup)


@app.command("show, s", help="Shows current applications")
def show_current_applications(
    live: Annotated[Optional[bool], typer.Option("-l", help=LIVE_HELP_TEXT)] = False,
    verbosity: Annotated[Optional[Verbosity], typer.Option("-v")] = Verbosity.SIMPLE.value,
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
        table_generator=lambda: generate_current_application_table(verbosity=verbosity, live=live),
    )


@app.command("create, c", help="Creates one or multiple apps based on a SLA")
def create_applications(
    sla_enum: AppSLAs,
    deploy: Annotated[
        bool, typer.Option("-d", help="Deploys the application service(s) afterwards.")
    ] = False,
) -> List[Application]:
    sla_file_name = f"{sla_enum}.SLA.json"
    SLA = ""
    with open(get_SLAs_path() / sla_file_name, "r") as f:
        SLA = json.load(f)
    sla_apps = SLA["applications"]
    sla_app_names = [app["application_name"] for app in sla_apps]
    # Note: The API endpoint returns all user apps and not just the newly posted ones.
    all_user_apps = custom_requests.CustomRequest(
        custom_requests.RequestCore(
            http_method=HttpMethod.POST,
            base_url=SYSTEM_MANAGER_URL,
            api_endpoint="/api/application",
            data=SLA,
        ),
        custom_requests.RequestAuxiliaries(
            what_should_happen=f"Create new application based on '{sla_enum}'",
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


@app.command("delete, d", help="Deletes all applications or only the specified one")
def delete_applications(
    app_id: Optional[ApplicationId] = typer.Argument(None, help="ID of the application to delete"),
) -> None:
    if app_id:
        delete_application(app_id)
        return

    for app in get_applications():
        delete_application(app["applicationID"])
