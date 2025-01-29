import getpass
import sys
from contextlib import nullcontext

import ansible_runner
import typer

from oak_cli.ansible.python_utils import CliPlaybook
from oak_cli.utils.common import run_in_shell
from oak_cli.utils.logging import logger
from oak_cli.utils.styling import create_spinner

ANSIBLE_GALAXY_ROLES = " ".join(("geerlingguy.docker", "gantsign.golang"))

app = typer.Typer()


@app.command(
    "fundamentals",
    help="""
    Install non-python fundamental dependencies like git, docker, docker compose plugin, etc.
    on the current machine
    """,
)
def install_fundamentals(
    show_ansible_output: bool = typer.Option(False, "--verbose"),
) -> None:
    # NOTE: The following playbook requires ansible-galaxy roles to be installed on the machine.
    # Installing it via a dedicated playbook does not work due to ansible-access right issues.
    run_in_shell(shell_cmd=f"ansible-galaxy install {ANSIBLE_GALAXY_ROLES}")
    become_password = getpass.getpass("[sudo] password: ")
    spinner_context = (
        create_spinner(message="Installing Dependencies")
        if not show_ansible_output
        else nullcontext()
    )
    with spinner_context:
        res = ansible_runner.run(
            playbook=CliPlaybook.INSTALL_FUNDAMENTALS.get_path(),
            extravars={"ansible_become_pass": become_password},
            quiet=not show_ansible_output,
        )
    if res.rc != 0:
        logger.fatal(
            "Dependency installation failed! Are you certain that you provided the correct password?"
        )
        sys.exit(1)

    logger.info("Dependencies successfully installed.")
