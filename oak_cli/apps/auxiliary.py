import rich

from oak_cli.apps.common import get_applications
from oak_cli.utils.styling import (
    OAK_GREEN,
    add_column,
    add_plain_columns,
    add_row_to_table,
    create_table,
)
from oak_cli.utils.types import Verbosity


def generate_current_application_table(verbosity: Verbosity, live: bool) -> rich.table.Table:
    table = create_table(
        caption="Current Applications",
        verbosity=verbosity,
        live=live,
    )
    add_column(table, column_name="Name", style=OAK_GREEN)
    add_plain_columns(table=table, column_names=["Services", "Application ID"])
    if verbosity == Verbosity.DETAILED:
        add_plain_columns(table=table, column_names=["Namespace", "User ID", "Description"])

    current_applications = get_applications()
    if not current_applications:
        return table

    for application in current_applications:
        special_row_items = []
        if verbosity == Verbosity.DETAILED:
            special_row_items += [
                application["application_namespace"],
                application["userId"],
                application["application_desc"],
            ]
        row_items = [
            application["application_name"],
            "(" + str(len(application["microservices"])) + ")",
            application["applicationID"],
        ] + special_row_items
        add_row_to_table(table=table, row_items=row_items)
    return table
