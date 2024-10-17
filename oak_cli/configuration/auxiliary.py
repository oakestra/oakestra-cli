import os
import pathlib
import readline
from typing import Optional

from oak_cli.utils.logging import logger


def prompt_for_path(
    path_name: str,
    promt_from_path: Optional[pathlib.Path] = None,
    promt_subject: str = "Path",
) -> pathlib.Path:
    if promt_from_path:
        os.chdir(promt_from_path)
    while True:
        logger.info(f"Please provide the '{path_name}'")
        # https://stackoverflow.com/questions/56119177/how-to-make-a-python-script-tab-complete-directories-in-terminal/56119373#56119373
        readline.set_completer_delims(" \t\n=")
        readline.parse_and_bind("tab: complete")
        user_typed_path = pathlib.Path(input(f"Enter {promt_subject} (tab complete support): "))
        if not user_typed_path.exists():
            logger.error("No file was found for the provided path!")
            continue
        break
    return user_typed_path
