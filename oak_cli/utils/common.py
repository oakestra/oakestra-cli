import pathlib
import shlex
import subprocess


def get_oak_cli_path() -> pathlib.Path:
    current_file = pathlib.Path(__file__).resolve()
    return current_file.parent.parent


def run_in_shell(
    shell_cmd: str,
    capture_output: bool = True,
    check: bool = True,
    text: bool = False,
    pure_shell: bool = False,
) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        shell_cmd if pure_shell else shlex.split(shell_cmd),
        capture_output=capture_output,
        check=check,
        text=text,
        shell=pure_shell,
    )
