import pathlib

from oak_cli.configuration.common import ConfigurableConfigKey, get_config_value


def get_flops_addon_repo_path() -> pathlib.Path:
    config_value = get_config_value(ConfigurableConfigKey.FLOPS_REPO_PATH)
    return pathlib.Path(config_value)
