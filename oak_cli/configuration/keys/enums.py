import enum


class ConfigKey:
    pass


class InternalConfigKey(ConfigKey, enum.Enum):
    """Interal Config Keys are not configurable by the user of the CLI."""

    CONFIG_MAIN_KEY = "OAK_CLI"
    CONFIG_VERSION = "config_version"


class ConfigurableConfigKey(ConfigKey, enum.Enum):
    LOCAL_MACHINE_PURPOSE = "local_machine_purpose"

    MAIN_OAK_REPO_PATH = "main_oak_repo_path"
    FLOPS_REPO_PATH = "flops_repo_path"

    SYSTEM_MANAGER_IP = "system_manager_ip"

    CLUSTER_MANAGER_IP = "cluster_manager_ip"
    CLUSTER_NAME = "cluster_name"
    CLUSTER_LOCATION = "cluster_location"

    def is_path(self) -> bool:
        return self.value.endswith("_path")

    def get_pleasant_name(self) -> str:
        return self.value.replace("_", " ")
