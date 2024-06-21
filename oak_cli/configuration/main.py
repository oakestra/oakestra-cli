import typer

import oak_cli.configuration.local_machine_purpose
import oak_cli.configuration.main_oak_repo
from oak_cli.utils.typer_augmentations import AliasGroup

app = typer.Typer(cls=AliasGroup)


app.add_typer(
    typer_instance=oak_cli.configuration.main_oak_repo.app,
    name="main-repo",
    help="Configure the main Oakestra repository",
)
app.add_typer(
    typer_instance=oak_cli.configuration.local_machine_purpose.app,
    name="local-machine-purpose",
    help="Manage the local machine purpose w.r.t. Oakestra",
)
