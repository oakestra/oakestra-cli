import typer

import oak_cli.configuration.local_machine_purpose
from oak_cli.utils.typer_augmentations import AliasGroup

app = typer.Typer(cls=AliasGroup)

app.add_typer(
    typer_instance=oak_cli.configuration.local_machine_purpose.app,
    name="lmp",
    help="Manage the local machine purpose w.r.t. Oakestra",
)
