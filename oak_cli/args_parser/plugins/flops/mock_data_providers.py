import argparse
from typing import Any

from oak_cli.commands.plugins.flops.main import create_new_mock_data_service
from oak_cli.commands.plugins.flops.SLAs.mocks.common import FLOpsMockDataProviderSLAs
from oak_cli.utils.types import Subparsers


def _aux_create_new_mock_data_service(args: Any) -> None:
    create_new_mock_data_service(args.sla)


def prepare_flops_mock_data_providers_argparser(flops_subparser: Subparsers) -> None:
    HELP_TEXT = "creates a new FLOps Mock-Data-Provider via the FLOps API"
    flops_projects_parser = flops_subparser.add_parser(
        "mock-data-provider",
        aliases=["m"],
        help=HELP_TEXT,
        description=HELP_TEXT,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    flops_projects_parser.add_argument(
        "sla",
        help="creates a FLOps project based on the specified SLA",
        type=FLOpsMockDataProviderSLAs,
        choices=FLOpsMockDataProviderSLAs,
        default=FLOpsMockDataProviderSLAs.MNIST_SIMPLE,
    )
    flops_projects_parser.set_defaults(func=_aux_create_new_mock_data_service)
