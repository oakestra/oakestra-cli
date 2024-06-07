import argparse
from typing import Any

from oak_cli.args_parser.plugins.flops.mock_data_providers import (
    prepare_flops_mock_data_providers_argparser,
)
from oak_cli.args_parser.plugins.flops.projects import prepare_flops_projects_argparser
from oak_cli.args_parser.plugins.flops.tracking import prepare_flops_tracking_argparser
from oak_cli.utils.types import Subparsers


def prepare_flops_argparsers(subparsers: Subparsers) -> None:
    flops_parser = subparsers.add_parser(
        "flops",
        aliases=["fl"],
        help="command for FLOps related activities",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    def flops_parser_print_help(_: Any) -> None:
        flops_parser.print_help()

    flops_parser.set_defaults(func=flops_parser_print_help)

    flops_subparser = flops_parser.add_subparsers(
        dest="FLOps commands",
    )

    prepare_flops_projects_argparser(flops_subparser)
    prepare_flops_mock_data_providers_argparser(flops_subparser)
    prepare_flops_tracking_argparser(flops_subparser)
