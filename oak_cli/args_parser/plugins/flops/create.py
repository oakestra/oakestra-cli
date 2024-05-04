import argparse
from typing import Any

from oak_cli.commands.plugins.flops.main import create_new_flops_project
from oak_cli.commands.plugins.flops.SLAs.common import FLOpsSLAs
from oak_cli.utils.types import Subparsers


def _aux_create_new_flops_project(args: Any) -> None:
    create_new_flops_project(args.sla)


def prepare_flops_create_argparser(flops_subparser: Subparsers) -> None:
    HELP_TEXT = "creates a new FLOps project - i.e. triggers the init FLOps API"
    flops_create_parser = flops_subparser.add_parser(
        "create",
        aliases=["c"],
        help=HELP_TEXT,
        description=HELP_TEXT,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    flops_create_parser.add_argument(
        "sla",
        help="creates a FLOps project based on the specified SLA",
        type=FLOpsSLAs,
        choices=FLOpsSLAs,
        default=FLOpsSLAs.CIFAR10_KERAS,
    )
    flops_create_parser.set_defaults(func=_aux_create_new_flops_project)
