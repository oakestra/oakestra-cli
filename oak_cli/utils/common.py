import enum
import os
import pathlib
import shlex
import subprocess
import sys

from oak_cli.utils.logging import logger


class CaptureOutputType(enum.Enum):
    TO_PYTHON_VAR = "to_python_var"
    TO_STDOUT = "to_stdout"
    HIDE_OUTPUT = "hide_output"


def get_oak_cli_path() -> pathlib.Path:
    current_file = pathlib.Path(__file__).resolve()
    return current_file.parent.parent


def run_in_shell(
    shell_cmd: str,
    capture_output_type: CaptureOutputType = CaptureOutputType.TO_PYTHON_VAR,
    check: bool = True,
    text: bool = False,
    # NOTE: subprocess.run usually expects an array of strings as the cmd.
    # It is not able to handle pipes ("|"), etc.
    # If shell=True is enabled then it expects a single string as cmd and can handle pipes, etc.
    pure_shell: bool = False,
) -> subprocess.CompletedProcess[bytes]:
    pipe_to_use = None
    if capture_output_type == CaptureOutputType.HIDE_OUTPUT:
        pipe_to_use = subprocess.DEVNULL

    return subprocess.run(
        shell_cmd if pure_shell else shlex.split(shell_cmd),
        capture_output=(capture_output_type == CaptureOutputType.TO_PYTHON_VAR),
        stdout=pipe_to_use,
        stderr=pipe_to_use,
        check=check,
        text=text,
        shell=pure_shell,
    )


def get_env_var(name: str, default: str = "") -> str:
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
