import argparse

from oak_cli.commands.apps.status import display_current_applications
from oak_cli.utils.types import Subparsers


def prepare_applications_display_argparser(applications_subparsers: Subparsers) -> None:
    HELP_TEXT = "displays the currently available/active applications"
    applications_status_parser = applications_subparsers.add_parser(
        "status",
        aliases=["s"],
        help=HELP_TEXT,
        description=HELP_TEXT,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    applications_status_parser.set_defaults(func=lambda _: display_current_applications())
