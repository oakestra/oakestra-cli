import argparse
from typing import Any

from oak_cli.commands.services.deployment import (
    deploy_new_instance,
    undeploy_all_instances_of_service,
    undeploy_instance,
)
from oak_cli.utils.types import Subparsers


def prepare_services_deployment_argparser(services_subparsers: Subparsers) -> None:
    HELP_TEXT = "deploys a service instance"
    services_deployment_parser = services_subparsers.add_parser(
        "deploy",
        aliases=["d"],
        help=HELP_TEXT,
        description=HELP_TEXT,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    services_deployment_parser.add_argument("service_id", type=str)
    services_deployment_parser.set_defaults(func=lambda args: deploy_new_instance(args.service_id))


def prepare_services_undeployment_argparser(services_subparsers: Subparsers) -> None:
    def _aux_undeploy(args: Any) -> None:
        if args.all:
            undeploy_all_instances_of_service(args.service_id)
        elif args.instancenumber:
            undeploy_instance(args.service_id, args.instancenumber)
        else:
            undeploy_instance(args.service_id)

    HELP_TEXT = "undeploys service instances"
    services_undeployment_parser = services_subparsers.add_parser(
        "undeploy",
        aliases=["u"],
        help=HELP_TEXT,
        description=HELP_TEXT,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    services_undeployment_parser.add_argument("service_id", type=str)
    services_undeployment_parser.add_argument(
        "--instancenumber",
        "-i",
        type=str,
    )
    services_undeployment_parser.add_argument(
        "-a", "--all", action="store_true", help="undeploy all instances of the service"
    )
    services_undeployment_parser.set_defaults(func=_aux_undeploy)
