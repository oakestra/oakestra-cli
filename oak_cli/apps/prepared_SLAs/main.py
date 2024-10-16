import shutil
import sys
from pathlib import Path
from typing import Optional

from oak_cli.configuration.auxiliary import prompt_for_path
from oak_cli.configuration.consts import OAK_CLI_SLA_FOLDER_PATH
from oak_cli.utils.logging import logger


def check_sla_folder() -> None:
    if not OAK_CLI_SLA_FOLDER_PATH.is_dir():
        OAK_CLI_SLA_FOLDER_PATH.mkdir(exist_ok=True)
        copy_over_prepared_slas()


def copy_over_prepared_slas() -> None:
    prepared_slas_folder = Path(__file__).resolve().parent

    for json_file in prepared_slas_folder.glob("*.json"):
        shutil.copy(json_file, OAK_CLI_SLA_FOLDER_PATH)


def get_sla_file_path(sla_file_name: Optional[str] = "") -> Path:
    if sla_file_name:
        sla_file_name = (
            sla_file_name if sla_file_name.endswith(".json") else sla_file_name + ".json"
        )
        sla_path = OAK_CLI_SLA_FOLDER_PATH / sla_file_name
        if not sla_path.is_file():
            logger.error(f"The SLA file '{sla_path}' does not exist.")
            sys.exit(1)
    else:
        relative_sla_file_path = prompt_for_path(
            "SLA File Name",
            promt_from_path=OAK_CLI_SLA_FOLDER_PATH,
            promt_subject="SLA file name",
        )
        sla_path = OAK_CLI_SLA_FOLDER_PATH / relative_sla_file_path
    return sla_path
