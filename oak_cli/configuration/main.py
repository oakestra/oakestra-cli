import pprint

import typer

import oak_cli.configuration.local_machine_purpose
import oak_cli.configuration.main_oak_repo
import oak_cli.docker.cluster_orchestrator
import oak_cli.docker.root_orchestrator
from oak_cli.configuration.common import check_and_handle_config_file, open_local_config
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


def configuration_expansion_help_text(
    configuration_cmd: str,
    add_hint_about_local_machine_purpose_configuration: bool = True,
) -> str:
    help = "\n".join(
        (
            "You can expand the available commands for this subcommand"
            " by configuring its related settings in the OAK-CLI.",
            f"The relevant command is '{configuration_cmd}'.",
        )
    )
    if add_hint_about_local_machine_purpose_configuration:
        help += "\n".join(
            (
                " By specifying the purpose of this machine you can unlock further CLI commands.",
                "You can do so by running 'oak c local-machine-purpose configure'.",
            )
        )
    return help


@app.command("show-config, s", help="Shows your current OAK-CLI configuration.")
def show_config():
    check_and_handle_config_file()
    config = open_local_config()
    for section in config.sections():
        pprint.pprint(dict(config.items(section)))
