import typer

from oak_cli.utils.common import run_in_shell
from oak_cli.utils.logging import logger
from oak_cli.utils.typer_augmentations import AliasGroup

app = typer.Typer(cls=AliasGroup)

CTR_CMD_PREFIX = "sudo ctr -n oakestra"


@app.command("delete-images", help="Deletes all local ctr images.")
def delete_all_local_ctr_images() -> None:
    shell_cmd_output = run_in_shell(
        pure_shell=True,
        shell_cmd=CTR_CMD_PREFIX + " images ls | awk '{print $1}' | tail -n +2",
        text=True,
    )
    image_names = shell_cmd_output.stdout.split()
    for image in image_names:
        shell_cmd_output = run_in_shell(shell_cmd=f"{CTR_CMD_PREFIX} images rm {image}")

    logger.info("All local ctr images have been deleted.")
