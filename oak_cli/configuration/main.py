import pprint
from typing import List, Optional

import typer
from icecream import ic
from typing_extensions import Annotated

import oak_cli.configuration.keys.main
import oak_cli.configuration.local_machine_purpose.main
import oak_cli.docker.cluster_orchestrator
import oak_cli.docker.root_orchestrator
from oak_cli.configuration.common import (
    OAK_CLI_CONFIG_PATH,
    check_and_handle_config_file,
    get_config_value,
    open_local_config,
    update_config_value,
)
from oak_cli.configuration.local_machine_purpose.enum import LocalMachinePurpose
from oak_cli.configuration.local_machine_purpose.main import set_local_machine_purposes
from oak_cli.utils.common import clear_file
from oak_cli.utils.typer_augmentations import AliasGroup

app = typer.Typer(cls=AliasGroup)


@app.command(
    "local-machine-purpose",
    help="\n".join(
        (
            "Configure the purpose of the local machine w.r.t. Oakestra.",
            "You can specify one or multiple purposes at once.",
            "E.g. ... --purpose A --purpose B",
        )
    ),
)
def configure_local_machine_purpose(
    # NOTE: Sets are not yet supported by the frameworks.
    # local_machine_purposes: Optional[List[LocalMachinePurpose]] = None,
    local_machine_purposes: Annotated[
        Optional[List[LocalMachinePurpose]],
        typer.Option("--purpose", help="A local machine purposes."),
    ] = None,
    show_explanation: bool = True,
) -> None:
    ic("hiiiiiiiiii")
    ic(local_machine_purposes)
    ic("chao")

    if local_machine_purposes:
        set_local_machine_purposes(set(local_machine_purposes))
        return

    if show_explanation:
        show_explanation = typer.confirm(
            "Do you want to learn more about OAK's local-machine-purposes?"
        )

    if show_explanation:
        ic(show_explanation, "blala explain ...")

    TODO cont

    # local_machine_purposes_set = set(local_machine_purposes)
    # if LocalMachinePurpose.EVERYTHING in local_machine_purposes_set:
    #     local_machine_purposes_set = {LocalMachinePurpose.EVERYTHING}
    # if LocalMachinePurpose.INITIAL in local_machine_purposes_set:
    #     local_machine_purposes_set = {LocalMachinePurpose.INITIAL}
    # check_and_handle_config_file()
    # update_config_value(
    #     key=ConfigurableConfigKey.LOCAL_MACHINE_PURPOSE,
    #     value=json.dumps([purpose.value for purpose in local_machine_purposes_set]),
    # )


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
