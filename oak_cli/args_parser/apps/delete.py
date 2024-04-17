import argparse
from typing import Any

from oak_cli.commands.apps.main import delete_all_applications, delete_application
from oak_cli.utils.types import Subparsers

_APP_ID_HELP_TEXT = """
if a (single) application ID is provided only that one app will be deleted
if 'all' is provided every application gets deleted"""

_DELETION_HELP_TEXT = "deletes one or all applications" + _APP_ID_HELP_TEXT


def prepare_applications_deletion_argparser(
    applications_subparsers: Subparsers,
) -> None:
    def aux_delete_applications(args: Any):
        if args.all or not args.app_id:
            delete_all_applications()
        else:
            delete_application(args.app_id)

    applications_deletion_parser = applications_subparsers.add_parser(
        "delete",
        aliases=["d"],
        help=_DELETION_HELP_TEXT,
        description=_DELETION_HELP_TEXT,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    applications_deletion_parser.add_argument(
        "-a", "--all", action="store_true", help="delete all applications"
    )
    applications_deletion_parser.add_argument("app_id", nargs="?", type=str, help=_APP_ID_HELP_TEXT)
    applications_deletion_parser.set_defaults(func=aux_delete_applications)
