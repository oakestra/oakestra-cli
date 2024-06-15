import subprocess
import time
from typing import Any, Callable, List

import rich
from rich.live import Live

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


def display_table(live: bool, table_generator: Callable[[Any], Any]) -> None:
    if not live:
        print_table(table=table_generator())
    else:
        # Clear the terminal to have the live-view in a clean isolated view.
        subprocess.run(["clear", "-x"])
        with Live(auto_refresh=False) as live:
            while True:
                live.update(table_generator(), refresh=True)
                time.sleep(LIVE_REFRESH_RATE)
