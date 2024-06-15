from typing import List

import rich

from oak_cli.utils.types import Verbosity

DEFAULT_JUSTIFY_DIRECTION = "left"
DEFAULT_CELL_OVERFLOW = "fold"

# Reference: https://rich.readthedocs.io/en/latest/appendix/colors.html
OAK_GREEN = "light_green"
OAK_GREY = "steel_blue"
OAK_BLUE = "cyan1"
OAK_WHITE = "white"


def create_table(
    caption: str = None,
    box: rich.box = rich.box.ROUNDED,
    show_lines: bool = True,
    verbosity: Verbosity = None,
) -> rich.table.Table:
    if verbosity:
        caption += f" (verbosity: '{verbosity.value}')"
    return rich.table.Table(
        caption=caption,
        box=box,
        show_lines=show_lines,
    )


def add_column(
    table: rich.table.Table,
    column_name: str,
    style: str = OAK_GREY,
    justify: str = DEFAULT_JUSTIFY_DIRECTION,
    overflow: str = DEFAULT_CELL_OVERFLOW,
) -> None:
    table.add_column(column_name, style=style, justify=justify, overflow=overflow)


def add_plain_columns(
    table: rich.table.Table,
    column_names: List[str],
) -> None:
    for name in column_names:
        add_column(table=table, column_name=name)


def print_table(table: rich.table.Table) -> None:
    rich.console.Console().print(table)
