#!/usr/bin/env python3
# PYTHON_ARGCOMPLETE_OK

from oak_cli.args_parser.main import parse_arguments_and_execute
from oak_cli.utils.argcomplete import handle_argcomplete


def main():
    handle_argcomplete()
    # Potential Future Work:
    # This implementation uses argparse & argcomplete for user friendly CLI behavior.
    # However especially argparse comes with a lot of additional boilerplate code.
    # It might be useful to look into more modern solutions for python CLI's like
    # https://github.com/pallets/click
    parse_arguments_and_execute()


if __name__ == "__main__":
    main()
