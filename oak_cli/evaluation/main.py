import sys
from typing import Optional

import ansible_runner
import typer

from oak_cli.addons.flops.SLAs.projects.common import FLOpsProjectSLAs
from oak_cli.ansible.python_utils import CLI_ANSIBLE_PATH, CliPlaybook
from oak_cli.evaluation.addons.flops.main import STAGE_FILE, TRAINED_MODEL_PERFORMANCE_CSV
from oak_cli.evaluation.common import (
    get_csv_dir_for_scenario,
    get_csv_file_path,
    get_pid_file_for_scenario,
    start_evaluation_process,
)
from oak_cli.evaluation.types import EvaluationScenario
from oak_cli.utils.common import (
    CaptureOutputType,
    clear_dir,
    clear_file,
    kill_process,
    run_in_shell,
)
from oak_cli.utils.logging import logger

app = typer.Typer()


@app.command(
    "start-manual-evaluation-run",
    help="Start the evaluation daemon (This command primarily exist for Ansible calls)",
)
def start_evaluation_run(
    scenario: EvaluationScenario = EvaluationScenario.RESOURCES.value,  # type: ignore
    evaluation_run_id: int = 1,
) -> None:
    start_evaluation_process(
        # NOTE: This strange enum handing is due to current Typer limitations.
        scenario=EvaluationScenario(scenario),
        evaluation_run_id=evaluation_run_id,
    )


@app.command(
    "start-automatic-evaluation-cycle",
    help="Execute multiple evaluation-runs automatically via Ansible",
)
def start_evaluation_cycle(
    scenario: EvaluationScenario = EvaluationScenario.RESOURCES.value,  # type: ignore
    number_of_evaluation_runs: int = 10,
    # NOTE: dicts are sadly not yet supported by typer.
    # extra_vars: dict = {},
    flops_project_type: Optional[FLOpsProjectSLAs] = None,
) -> None:
    scenario = EvaluationScenario(scenario)
    extra_vars = {}
    extra_vars["number_of_evaluation_runs"] = number_of_evaluation_runs
    if flops_project_type:
        extra_vars["flops_project_type"] = flops_project_type.value

    match scenario:
        case EvaluationScenario.RESOURCES:
            # NOTE:
            # This playbook requires ansible-galaxy dependencies to be installed on the machine.
            # Installing it via a dedicated playbook does not work
            # due to ansible-access right issues.
            run_in_shell(shell_cmd="ansible-galaxy collection install community.docker")
            ansible_runner.run(
                project_dir=str(CLI_ANSIBLE_PATH),
                playbook=CliPlaybook.EVALUATE_RESOURCES.get_path(),
                extravars=extra_vars,
            )
        case EvaluationScenario.FLOPS_MONOLITH:
            ansible_runner.run(
                project_dir=str(CLI_ANSIBLE_PATH),
                playbook=CliPlaybook.EVALUATE_FLOPS_MONOLITH.get_path(),
                extravars=extra_vars,
            )

        case EvaluationScenario.FLOPS_MULTI_CLUSTER:
            ansible_runner.run(
                project_dir=str(CLI_ANSIBLE_PATH),
                playbook=CliPlaybook.EVALUATE_FLOPS_MULTI_CLUSTER.get_path(),
                extravars=extra_vars,
            )


@app.command("show-csv")
def show_csv(
    live: bool = False,
    evaluation_run_id: int = 1,
    scenario: EvaluationScenario = EvaluationScenario.RESOURCES.value,  # type: ignore
) -> None:
    scenario = EvaluationScenario(scenario)
    csv_file = get_csv_file_path(
        csv_dir=get_csv_dir_for_scenario(scenario), evaluation_run_id=evaluation_run_id
    )
    if not csv_file.exists():
        logger.warning(f"The file '{csv_file}' does not exist.")
        sys.exit(1)

    run_in_shell(
        shell_cmd=f"tail -f {csv_file}" if live else f"cat {csv_file}",
        capture_output_type=CaptureOutputType.TO_STDOUT,
    )


@app.command("clean")
def clean_up(
    scenario: EvaluationScenario = EvaluationScenario.RESOURCES.value,  # type: ignore
) -> None:
    """Cleans any remaining artifacts to be ready for a fresh new evaluation-cycle.
    This function should not be called between evaluation-runs.
    - Clears the contents of the PID and CSV files.
    - Kills any daemons.
    """
    scenario = EvaluationScenario(scenario)
    clear_dir(get_csv_dir_for_scenario(scenario))
    if scenario in [EvaluationScenario.FLOPS_MONOLITH, EvaluationScenario.FLOPS_MULTI_CLUSTER]:
        clear_file(STAGE_FILE)
        clear_file(TRAINED_MODEL_PERFORMANCE_CSV)
    stop_evaluation_run(scenario=scenario)


@app.command("stop-evaluation-run")
def stop_evaluation_run(
    scenario: EvaluationScenario = EvaluationScenario.RESOURCES.value,  # type: ignore
) -> None:
    """Stops the current evaluation-run.
    - Kills its daemon
    - Clears its PID file contents
    """
    scenario = EvaluationScenario(scenario)
    pidfile = get_pid_file_for_scenario(scenario)
    if not pidfile.exists():
        logger.debug(f"The file '{pidfile}' does not exist.")
        return
    if pidfile.stat().st_size == 0:
        logger.debug(f"The file '{pidfile}' is empty.")
        return

    with open(pidfile, "r") as file:
        pid = int(file.readline())
    kill_process(pid)
    clear_file(pidfile)

    if scenario in [EvaluationScenario.FLOPS_MONOLITH, EvaluationScenario.FLOPS_MULTI_CLUSTER]:
        clear_file(STAGE_FILE)
