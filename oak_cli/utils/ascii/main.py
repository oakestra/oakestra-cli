from rich.console import Console

# from rich.style import Style
from rich_pixels import Pixels

from oak_cli.utils.ascii.oakestra_logo import OAKESTRA_ASCII_LOGO, OAKESTRA_LOGO_COLOR_MAP


def print_oakestra_logo() -> None:
    console = Console()
    # pixels = Pixels.from_ascii(grid, mapping)
    pixels = Pixels.from_ascii(OAKESTRA_ASCII_LOGO, OAKESTRA_LOGO_COLOR_MAP)
    console.print(pixels)
