import json
from typing import List, Optional

import rich
import typer
from icecream import ic
from typing_extensions import Annotated

import oak_cli.utils.api.custom_requests as custom_requests
from oak_cli.apps.common import delete_application, get_applications
from oak_cli.apps.SLAs.common import AppSLAs, get_SLAs_path
from oak_cli.commands.services.deployment import deploy_new_instance
from oak_cli.utils.api.common import SYSTEM_MANAGER_URL
from oak_cli.utils.api.custom_http import HttpMethod
from oak_cli.utils.exceptions.types import OakCLIExceptionTypes
from oak_cli.utils.styling import (
    OAK_GREEN,
    add_column,
    add_plain_columns,
    create_table,
    print_table,
)
from oak_cli.utils.typer_augmentations import AliasGroup
from oak_cli.utils.types import Application, ApplicationId, Verbosity

app = typer.Typer(cls=AliasGroup)


@app.command("show, s", help="Shows current applications")
def show_current_applications(
    verbosity: Annotated[Optional[Verbosity], typer.Option("-v")] = Verbosity.SIMPLE.value,
) -> None:
    current_applications = get_applications()
    if not current_applications:
        return

    table = create_table(caption="Current Applications", verbosity=verbosity)
    add_column(table, column_name="Name", style=OAK_GREEN)
    add_plain_columns(table=table, column_names=["Services", "Application ID"])
    if verbosity == Verbosity.DETAILED:
        add_plain_columns(table=table, column_names=["Namespace", "User ID", "Description"])

    for i, application in enumerate(current_applications):
        special_row_elements = []
        match verbosity:
            case Verbosity.EXHAUSTIVE:
                ic(i, application)
                continue
            case Verbosity.DETAILED:
                special_row_elements += [
                    application["application_namespace"],
                    application["userId"],
                    application["application_desc"],
                ]

        row_elements = [
            application["application_name"],
            "(" + str(len(application["microservices"])) + ")",
            application["applicationID"],
        ] + special_row_elements
        table.add_row(*row_elements)

    if verbosity == Verbosity.EXHAUSTIVE:
        return

    print_table(table)


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
                deploy_new_instance(service_id)

    return newly_added_apps


@app.command("delete, d", help="Deletes all applications or only the specified one")
def delete_applications(
    app_id: Optional[ApplicationId] = typer.Option(None, help="ID of the application to delete"),
) -> None:
    if app_id:
        delete_application(app_id)
        return

    for app in get_applications():
        delete_application(app["applicationID"])
