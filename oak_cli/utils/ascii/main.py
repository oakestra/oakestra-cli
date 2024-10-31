from rich.console import Console

# from rich.style import Style
from rich_pixels import Pixels

from oak_cli.utils.ascii.init_welcome import WELCOME_ASCII_LOGO, WELCOME_COLOR_MAP
from oak_cli.utils.ascii.oakestra_logo import OAKESTRA_ASCII_LOGO, OAKESTRA_LOGO_COLOR_MAP


def _print_ascii(pattern, color_map) -> None:
    console = Console()
    pixels = Pixels.from_ascii(pattern, color_map)
    console.print(pixels)


def print_oakestra_logo() -> None:
    _print_ascii(OAKESTRA_ASCII_LOGO, OAKESTRA_LOGO_COLOR_MAP)


def print_welcome_logo() -> None:
    _print_ascii(WELCOME_ASCII_LOGO, WELCOME_COLOR_MAP)
