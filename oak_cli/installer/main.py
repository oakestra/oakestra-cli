import ansible_runner
import typer

from oak_cli.ansible.python_utils import CLI_PLAYBOOK
from oak_cli.utils.common import run_in_shell

app = typer.Typer()


@app.command(
    "fundamentals",
    help="""
    Installs non-python fundamental dependencies like git, docker, docker-compose, etc.
    on the current machine.
    """,
)
def install_fundamentals() -> None:
    # NOTE: The following playbook requires a ansible-galaxy role to be installed on the machine.
    # Installing it via a dedicated playbook does not work due to ansible-access right issues.
    run_in_shell(shell_cmd="ansible-galaxy install geerlingguy.docker")
    r = ansible_runner.run(playbook=CLI_PLAYBOOK.INSTALL_ANSIBLE_GALAXY_DEPENDENCIES.get_path())
    # r = ansible_runner.run(playbook=CLI_PLAYBOOK.INSTALL_FUNDAMENTALS.get_path())
    from icecream import ic

    ic(r.status, r.rc)
