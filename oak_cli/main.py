#!/usr/bin/env python3
# PYTHON_ARGCOMPLETE_OK

from oak_cli.args_parser.main import parse_arguments_and_execute
from oak_cli.utils.argcomplete import handle_argcomplete


def main():
    handle_argcomplete()
    parse_arguments_and_execute()


if __name__ == "__main__":
    main()
