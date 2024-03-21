import shlex
import subprocess


def handle_argcomplete() -> None:
    # Note: Ideally this would only occur once in a dedicated postinstall script
    # (similar to debian packages).
    # However, python packages do not seem to allow postinstall scripts.
    # The argcomplete command also is not too customizable to check if it is already installed,
    # because it might behave differently depending on the OS.
    with open("/dev/null", "w") as devnull:
        subprocess.run(
            shlex.split("activate-global-python-argcomplete -y --user"),
            stdout=devnull,
            stderr=devnull,
        )
