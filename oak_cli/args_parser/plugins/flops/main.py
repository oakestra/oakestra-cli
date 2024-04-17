import argparse
from typing import Any

from oak_cli.args_parser.plugins.flops.create import prepare_flops_create_argparser
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

    prepare_flops_create_argparser(flops_subparser)
