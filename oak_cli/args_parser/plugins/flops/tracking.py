import argparse

from oak_cli.commands.plugins.flops.main import get_tracking_url
from oak_cli.utils.types import Subparsers


def prepare_flops_tracking_argparser(flops_subparser: Subparsers) -> None:
    HELP_TEXT = "gets the tracking server URL"
    flops_tracking_parser = flops_subparser.add_parser(
        "tracking",
        aliases=["t"],
        help=HELP_TEXT,
        description=HELP_TEXT,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    flops_tracking_parser.set_defaults(func=lambda _: get_tracking_url())
