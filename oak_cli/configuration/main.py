import pprint

import typer

import oak_cli.configuration.keys.main
import oak_cli.configuration.local_machine_purpose.main
import oak_cli.docker.cluster_orchestrator
import oak_cli.docker.root_orchestrator
from oak_cli.configuration.common import (
    OAK_CLI_CONFIG_PATH,
    check_and_handle_config_file,
    open_local_config,
)
from oak_cli.utils.common import clear_file
from oak_cli.utils.typer_augmentations import AliasGroup

app = typer.Typer(cls=AliasGroup)

app.add_typer(
    typer_instance=oak_cli.configuration.local_machine_purpose.main.app,
    name="local-machine-purpose",
    help="Manage the local machine purpose w.r.t. Oakestra",
)

app.add_typer(
    typer_instance=oak_cli.configuration.keys.main.app,
    name="key-vars",
    help="Configure OAK-CLI Key Variables",
)


@app.command("show-config, s", help="Shows your current OAK-CLI configuration.")
def show_config():
    check_and_handle_config_file()
    config = open_local_config()
    for section in config.sections():
        pprint.pprint(dict(config.items(section)))


@app.command("reset-config", help="Resets your current OAK-CLI configuration to its initial state.")
def reset_config():
    clear_file(OAK_CLI_CONFIG_PATH)
    # config = open_local_config()
    # config.clear()
    check_and_handle_config_file()
