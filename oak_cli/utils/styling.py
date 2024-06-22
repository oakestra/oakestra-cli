import time
from typing import Any, Callable, List, Union

import rich
from rich.live import Live

from oak_cli.utils.common import run_in_shell
from oak_cli.utils.types import Verbosity

LIVE_REFRESH_RATE = 3  # Seconds
LIVE_HELP_TEXT = "Use dynamic Live-Display. (Exit view e.g. via 'Ctr+c')"
LIVE_VIEW_PREFIX = "LIVE-VIEW: "


DEFAULT_JUSTIFY_DIRECTION = "left"
DEFAULT_CELL_OVERFLOW = "fold"

# Reference: https://rich.readthedocs.io/en/latest/appendix/colors.html
OAK_GREEN = "light_green"
OAK_GREY = "steel_blue"
OAK_BLUE = "cyan1"
OAK_WHITE = "white"


def add_row_to_table(table: rich.table.Table, row_items: Union[Any, list[Any]]) -> None:
    if not isinstance(row_items, list):
        row_items = [row_items]
    aligned_row_items = [rich.align.Align(item or "-", vertical="middle") for item in row_items]
    table.add_row(*aligned_row_items)


def create_spinner(message: str, style: str = OAK_GREEN):  # NOTE: The return type is complex.
    """Returns a spinner object that should be used via a 'with'"""
    return rich.console.Console().status(f"[{style}]{message}")


def create_table(
    title: str = None,
    caption: str = None,
    box: rich.box = rich.box.ROUNDED,
    show_lines: bool = True,
    verbosity: Verbosity = None,
    live: bool = False,
    pad_edge=True,
    padding: Union[int, tuple] = (0, 1),
    show_header: bool = True,
) -> rich.table.Table:
    if verbosity:
        caption += f" (verbosity: '{verbosity.value}')"
    if live:
        LIVE_PREFIX = "🔄️ LIVE"
        caption = f"{LIVE_PREFIX} - {caption}" if caption else LIVE_PREFIX
    return rich.table.Table(
        title=title,
        caption=caption,
        box=box,
        show_lines=show_lines,
        pad_edge=pad_edge,
        collapse_padding=(verbosity == Verbosity.DETAILED),
        padding=padding,
        show_header=show_header,
    )


def add_column(
    table: rich.table.Table,
    column_name: str,
    style: str = OAK_GREY,
    justify: str = DEFAULT_JUSTIFY_DIRECTION,
    overflow: str = DEFAULT_CELL_OVERFLOW,
    no_wrap: bool = False,
) -> None:
    table.add_column(
        column_name,
        style=style,
        justify=justify,
        overflow=overflow,
        no_wrap=no_wrap,
    )


def add_plain_columns(
    table: rich.table.Table,
    column_names: List[str],
) -> None:
    for name in column_names:
        add_column(table=table, column_name=name)


def print_table(table: rich.table.Table) -> None:
    rich.console.Console().print(table)


def display_table(live: bool, table_generator: Callable[[Any], Any]) -> None:
    if not live:
        print_table(table=table_generator())
    else:
        # Clear the terminal to have the live-view in a clean isolated view.
        run_in_shell(shell_cmd="clear -x", check=False, capture_output=False)
        with Live(auto_refresh=False) as live:
            while True:
                live.update(table_generator(), refresh=True)
                time.sleep(LIVE_REFRESH_RATE)
