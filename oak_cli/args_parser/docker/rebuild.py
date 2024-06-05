import argparse
from typing import Any

from oak_cli.commands.docker.enums import ClusterOrchestratorService, RootOrchestratorService
from oak_cli.commands.docker.rebuild import rebuild_docker_service
from oak_cli.commands.docker.restart import restart_docker_service
from oak_cli.utils.types import Subparsers

_CACHE_LESS_REBUILDS_HELP = """
rebuilds the images without (layer) caching.
Is useful when e.g. local oakestra library dependencies change,
because these libraries are not references by a specific version, thus
the requirements.txt file stays the same even though the underlying dependencies changed.
This flag runs an additional docker-compose-build command before the main docker-compose-up one.
Using this flag leads to a longer execution time, thus only use it when necessary.
"""


def aux_rebuild_docker_service(args: Any):
    if args.only_restart:
        restart_docker_service(args.service)
    else:
        rebuild_docker_service(docker_service=args.service, cache_less=args.cache_less_rebuild)


def prepare_docker_rebuild_root_orchestrator_service_parser(
    docker_rebuild_subparser: Subparsers,
) -> None:
    docker_rebuild_root_orchestrator_service_parser = docker_rebuild_subparser.add_parser(
        "root_orchestrator",
        aliases=["ro"],
    )
    docker_rebuild_root_orchestrator_service_parser.add_argument(
        "service",
        help="testing",
        type=RootOrchestratorService,
        choices=RootOrchestratorService,
    )
    docker_rebuild_root_orchestrator_service_parser.set_defaults(func=aux_rebuild_docker_service)


def prepare_docker_rebuild_cluster_orchestrator_service_parser(
    docker_rebuild_subparser: Subparsers,
) -> None:
    docker_rebuild_cluster_orchestrator_service_parser = docker_rebuild_subparser.add_parser(
        "cluster_orchestrator",
        aliases=["co"],
    )
    docker_rebuild_cluster_orchestrator_service_parser.add_argument(
        "service",
        help="testing",
        type=ClusterOrchestratorService,
        choices=ClusterOrchestratorService,
    )
    docker_rebuild_cluster_orchestrator_service_parser.set_defaults(func=aux_rebuild_docker_service)


def prepare_docker_rebuild_argparser(docker_subparsers: Subparsers) -> None:
    HELP_TEXT = "rebuilds a docker compose service"
    docker_restart_parser = docker_subparsers.add_parser(
        "rebuilds",
        aliases=["r"],
        help=HELP_TEXT,
        description=HELP_TEXT,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    docker_restart_parser.add_argument(
        "-o",
        "--only-restart",
        help="only restart without rebuilding the service",
        action="store_true",
    )
    docker_restart_parser.add_argument(
        "-c",
        "--cache-less-rebuild",
        help=_CACHE_LESS_REBUILDS_HELP,
        action="store_true",
    )
    docker_restart_subparsers = docker_restart_parser.add_subparsers()
    prepare_docker_rebuild_root_orchestrator_service_parser(docker_restart_subparsers)
    prepare_docker_rebuild_cluster_orchestrator_service_parser(docker_restart_subparsers)
