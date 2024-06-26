from typing import Optional

import typer

from oak_cli.configuration.auxiliary import prompt_for_path
from oak_cli.configuration.common import check_and_handle_config_file, update_config_value
from oak_cli.configuration.keys.enums import ConfigurableConfigKey

app = typer.Typer()


@app.command("configure", help="Configure a core variable.")
def configure_config_key(key: ConfigurableConfigKey, value: Optional[str] = None) -> None:
    check_and_handle_config_file()
    if not value:
        if key.is_path():
            value = str(prompt_for_path(key.get_pleasant_name()))
        else:
            value = typer.prompt(f"What values should '{key.get_pleasant_name()}' have?")
    update_config_value(key=key, value=value)
