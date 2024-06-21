import pathlib
import shlex
import subprocess


def get_oak_cli_path() -> pathlib.Path:
    current_file = pathlib.Path(__file__).resolve()
    return current_file.parent.parent


def run_in_shell(
    shell_cmd: str,
    capture_output=True,
    check=True,
    text=False,
) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        shlex.split(shell_cmd), capture_output=capture_output, check=check, text=text
    )
