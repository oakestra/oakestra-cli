import ansible_runner
import typer

from oak_cli.ansible.python_utils import CLI_ANSIBLE_PATH, CliPlaybook
from oak_cli.evaluation.localhost_resources.metrics import start_evaluation_run_daemon
from oak_cli.utils.common import run_in_shell

app = typer.Typer()


def start_evaluation_run(evaluation_run_id: int = 1) -> None:
    start_evaluation_run_daemon(evaluation_run_id)


@app.command("start")
def start_evaluation_cycle(number_of_evaluation_runs: int = 10) -> None:
    # NOTE: This playbook requires ansible-galaxy dependencies to be installed on the machine.
    # Installing it via a dedicated playbook does not work due to ansible-access right issues.
    run_in_shell(shell_cmd="ansible-galaxy collection install community.docker")
    ansible_runner.run(
        project_dir=str(CLI_ANSIBLE_PATH),
        playbook=CliPlaybook.EVALUATE_LOCALHOST.get_path(),
        extravars={"number_of_evaluation_runs": number_of_evaluation_runs},
    )
