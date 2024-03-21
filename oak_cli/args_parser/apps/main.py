import argparse
from typing import Any

from oak_cli.args_parser.apps.create import prepare_applications_create_argparser
from oak_cli.args_parser.apps.delete import prepare_applications_deletion_argparser
from oak_cli.args_parser.apps.status import prepare_applications_display_argparser
from oak_cli.utils.types import Subparsers


def prepare_applications_argparsers(subparsers: Subparsers) -> None:
    applications_parser = subparsers.add_parser(
        "applications",
        aliases=["a"],
        help="command for application(s) related activities",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    def applications_parser_print_help(_: Any) -> None:
        applications_parser.print_help()

    applications_parser.set_defaults(func=applications_parser_print_help)

    applications_subparsers = applications_parser.add_subparsers(
        dest="applications commands",
    )

    prepare_applications_create_argparser(applications_subparsers)
    prepare_applications_display_argparser(applications_subparsers)
    prepare_applications_deletion_argparser(applications_subparsers)
