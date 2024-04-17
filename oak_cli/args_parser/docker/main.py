import argparse
from typing import Any

from oak_cli.args_parser.docker.rebuild import prepare_docker_rebuild_argparser
from oak_cli.utils.types import Subparsers


def prepare_docker_argparsers(subparsers: Subparsers) -> None:
    docker_parser = subparsers.add_parser(
        "docker",
        aliases=["d"],
        help="command for docker(compose) related activities",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    def docker_parser_print_help(_: Any) -> None:
        docker_parser.print_help()

    docker_parser.set_defaults(func=docker_parser_print_help)

    docker_subparsers = docker_parser.add_subparsers(
        dest="services commands",
    )

    prepare_docker_rebuild_argparser(docker_subparsers)
