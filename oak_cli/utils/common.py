import os
import pathlib
import shlex
import subprocess
import sys
from typing import Union

from oak_cli.utils.logging import logger


def get_oak_cli_path() -> pathlib.Path:
    current_file = pathlib.Path(__file__).resolve()
    return current_file.parent.parent


def run_in_shell(
    shell_cmd: str,
    capture_output: bool = True,
    check: bool = True,
    text: bool = False,
    # NOTE: subprocess.run usually expects an array of strings as the cmd.
    # It is not able to handle pipes ("|"), etc.
    # If shell=True is enabled then it expects a single string as cmd and can handle pipes, etc.
    pure_shell: bool = False,
) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        shell_cmd if pure_shell else shlex.split(shell_cmd),
        capture_output=capture_output,
        check=check,
        text=text,
        shell=pure_shell,
    )


def get_env_var(name: str, default: Union[str, int] = None) -> str:
    env_var = os.environ.get(name) or default
    if env_var is None:
        _ERROR_MESSAGE = "\n".join(
            (
                "Terminating.",
                "Make sure to set the environment variables first.",
                f"Missing: '{name}'",
            )
        )
        logger.fatal(f"{_ERROR_MESSAGE}'{name}'")
        sys.exit(1)
    return env_var
