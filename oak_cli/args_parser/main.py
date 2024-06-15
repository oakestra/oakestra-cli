# PYTHON_ARGCOMPLETE_OK

import argparse

import argcomplete

from oak_cli.args_parser.docker.main import prepare_docker_argparsers
from oak_cli.args_parser.plugins.main import prepare_plugins_argparsers


def parse_arguments_and_execute() -> None:
    parser = argparse.ArgumentParser()

    # 'dest' & 'required' are needed to ensure correct behavior if no arguments are passed.
    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    prepare_plugins_argparsers(subparsers)
    prepare_docker_argparsers(subparsers)  # WIP

    argcomplete.autocomplete(parser)
    args = parser.parse_args()
    args.func(args)
