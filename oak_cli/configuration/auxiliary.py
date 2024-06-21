from oak_cli.utils.types import CustomEnum


class ConfigKey(CustomEnum):
    CONFIG_MAIN_KEY = "OAK_CLI"
    CONFIG_VERSION_KEY = "config_version"

    MAIN_OAK_REPO_PATH_KEY = "main_oak_repo_path"
    LOCAL_MACHINE_PURPOSE_KEY = "local_machine_purpose"
