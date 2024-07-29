import typer

import oak_cli.evaluation.resources.main as resources
from oak_cli.evaluation.common import start_evaluation_run_daemon
from oak_cli.utils.typer_augmentations import typer_help_text

app = typer.Typer()

app.add_typer(
    typer_instance=resources.app,
    name="resources",
    help=typer_help_text("resources"),
)


@app.command("start-manual-evaluation-run")
def start_evaluation_run(evaluation_run_id: int = 1) -> None:
    start_evaluation_run_daemon(evaluation_run_id)
