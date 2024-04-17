import argparse
from typing import Any

from oak_cli.args_parser.plugins.flops.main import prepare_flops_argparsers
from oak_cli.utils.types import Subparsers


def prepare_plugins_argparsers(subparsers: Subparsers) -> None:
    plugins_parser = subparsers.add_parser(
        "plugins",
        aliases=["p"],
        help="command for plugin related activities",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    def plugins_parser_print_help(_: Any) -> None:
        plugins_parser.print_help()

    plugins_parser.set_defaults(func=plugins_parser_print_help)

    plugins_subparsers = plugins_parser.add_subparsers(
        dest="plugins commands",
    )

    prepare_flops_argparsers(plugins_subparsers)
