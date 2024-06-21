import configparser

import typer

from oak_cli.configuration.auxiliary import ConfigKey
from oak_cli.configuration.common import (
    check_and_handle_config_file,
    configure_aspect,
    get_config_value,
    open_local_config,
)
from oak_cli.utils.typer_augmentations import AliasGroup
from oak_cli.utils.types import CustomEnum

app = typer.Typer(cls=AliasGroup)


class LocalMachinePurpose(CustomEnum):
    """A machine can have one, multiple, or all of these purposes."""

    ROOT_ORCHESTRATOR = "root_orchestrator"
    CLUSTER_ORCHESTRATOR = "cluster_orchestrator"
    WORKER_NODE = "worker_node"


def get_local_machine_purpose_from_config(
    config: configparser.ConfigParser,
) -> LocalMachinePurpose:
    local_machine_purpose = get_config_value(config, ConfigKey.LOCAL_MACHINE_PURPOSE_KEY)
    return LocalMachinePurpose(local_machine_purpose)


@app.command(
    "configure",
    help="Configure the purpose of the local machine w.r.t. Oakestra.",
)
def configure_local_machine_purpose() -> None:
    check_and_handle_config_file()
    configure_aspect(
        aspect=LocalMachinePurpose,
        configuration_text="local machine purpose",
        config_key=ConfigKey.LOCAL_MACHINE_PURPOSE_KEY,
        use_default=False,
    )


# @app.command(
#     "configure",
#     help="Configure the purpose of the local machine w.r.t. Oakestra.",
# )
# def configure_local_machine_purpose() -> None:
#     config = configparser.ConfigParser()
#     config[ConfigKey.CONFIG_MAIN_KEY.value] = {}
#     config = set_config_value(config, ConfigKey.CONFIG_MAIN_KEY, CONFIG_VERSION)
#     config = configure_aspect(
#         config=config,
#         aspect=LocalMachinePurpose,
#         configuration_text="local machine purpose",
#         config_key=ConfigKey.LOCAL_MACHINE_PURPOSE_KEY,
#         use_default=False,
#     )
#     with open(OAK_CLI_CONFIG_PATH, "w") as config_file:
#         config.write(config_file)

# def configure_package_manually(_) -> None:
#     # Check if the calling user has permissions to override the package's configuration.
#     if os.getuid() != 0:
#         try:
#             subprocess.run(["sudo", "python3", sys.argv[0], *sys.argv[1:]], check=True)
#         except subprocess.CalledProcessError as error:
#             logger.error(
#                 f"An error occurred while running the 'configure' command with sudo: {error}"
#             )
#             sys.exit(1)
#         return

# configure_package()
# logger.info("Preferences saved.")
