import argparse
from typing import Any

from oak_cli.commands.apps.main import send_sla
from oak_cli.commands.services.deployment import deploy_new_instance
from oak_cli.utils.SLAs.common import KnownSLA
from oak_cli.utils.types import Subparsers


def _aux_create_application(args: Any) -> None:
    apps = send_sla(args.sla)
    if args.deploy:
        for app in apps:
            for service_id in app["microservices"]:
                deploy_new_instance(service_id)


def prepare_applications_create_argparser(applications_subparsers: Subparsers) -> None:
    HELP_TEXT = "creates a new application"
    applications_create_parser = applications_subparsers.add_parser(
        "create",
        aliases=["c"],
        help=HELP_TEXT,
        description=HELP_TEXT,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    applications_create_parser.add_argument(
        "-d",
        "--deploy",
        action="store_true",
        help="deploy all services of the provided application(s)",
    )
    applications_create_parser.add_argument(
        "sla",
        help="creates an application based on a KnowsSLA (if is has its own enum)",
        type=KnownSLA,
        choices=KnownSLA,
        default=KnownSLA.DEFAULT,
    )
    applications_create_parser.set_defaults(func=_aux_create_application)
