import typer
from icecream import ic

from oak_cli.utils.common import run_in_shell
from oak_cli.utils.typer_augmentations import AliasGroup

app = typer.Typer(cls=AliasGroup)


@app.command("delete-images", help="Deletes all local ctr images.")
def delete_all_local_ctr_images() -> None:
    local_ctr_image_output = run_in_shell(shell_cmd="sudo ctr -n oakestra images ls", text=True)
    ic(local_ctr_image_output)
