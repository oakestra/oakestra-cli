import ansible_runner
import typer

from oak_cli.ansible.python_utils import CLI_ANSIBLE_PATH, CliPlaybook

app = typer.Typer()


@app.command("start")
def start_evaluation_cycle(number_of_evaluation_runs: int = 10) -> None:
    ansible_runner.run(
        project_dir=str(CLI_ANSIBLE_PATH),
        playbook=CliPlaybook.EVALUATE_FLOPS.get_path(),
        extravars={"number_of_evaluation_runs": number_of_evaluation_runs},
    )
