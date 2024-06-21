import ansible_runner
import typer

from oak_cli.ansible.python_utils import CliPlaybook
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
    ansible_runner.run(playbook=CliPlaybook.INSTALL_FUNDAMENTALS.get_path())
