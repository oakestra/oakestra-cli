from oak_cli.configuration.common import get_config_value
from oak_cli.configuration.keys.enums import ConfigurableConfigKey


def get_system_manager_url() -> str:
    system_manager_ip = get_config_value(ConfigurableConfigKey.SYSTEM_MANAGER_IP)
    return f"http://{system_manager_ip}:10000"
