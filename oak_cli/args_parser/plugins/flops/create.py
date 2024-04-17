import argparse

from oak_cli.commands.plugins.flops.main import create_new_fl_service
from oak_cli.utils.types import Subparsers


def prepare_flops_create_argparser(flops_subparser: Subparsers) -> None:
    HELP_TEXT = "creates a new FLOps project - i.e. triggers the init FLOps API"
    flops_create_parser = flops_subparser.add_parser(
        "create",
        aliases=["c"],
        help=HELP_TEXT,
        description=HELP_TEXT,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    flops_create_parser.set_defaults(func=lambda _: create_new_fl_service())
