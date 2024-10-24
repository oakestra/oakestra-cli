import pathlib
import shutil
import sys
from pathlib import Path
from typing import Optional

from oak_cli.configuration.auxiliary import prompt_for_path
from oak_cli.configuration.consts import OAK_CLI_USER_FOLDER_PATH
from oak_cli.utils.logging import logger

OAK_CLI_FLOPS_FOLDER_PATH = OAK_CLI_USER_FOLDER_PATH / "addons" / "flops"
OAK_CLI_FLOPS_PROJECT_SLA_FOLDER_PATH = OAK_CLI_FLOPS_FOLDER_PATH / "projects"
OAK_CLI_FLOPS_MOCKS_SLA_FOLDER_PATH = OAK_CLI_FLOPS_FOLDER_PATH / "mocks"


def check_flops_folders() -> None:
    if not OAK_CLI_FLOPS_FOLDER_PATH.is_dir():
        OAK_CLI_FLOPS_FOLDER_PATH.mkdir(exist_ok=True, parents=True)

    parent_dir = Path(__file__).resolve().parent

    if not OAK_CLI_FLOPS_PROJECT_SLA_FOLDER_PATH.is_dir():
        OAK_CLI_FLOPS_PROJECT_SLA_FOLDER_PATH.mkdir(exist_ok=True, parents=True)
        copy_over_prepared_slas(
            prepared_slas_folder_path=parent_dir / "projects",
            target_path=OAK_CLI_FLOPS_PROJECT_SLA_FOLDER_PATH,
        )

    if not OAK_CLI_FLOPS_MOCKS_SLA_FOLDER_PATH.is_dir():
        OAK_CLI_FLOPS_MOCKS_SLA_FOLDER_PATH.mkdir(exist_ok=True, parents=True)
        copy_over_prepared_slas(
            prepared_slas_folder_path=parent_dir / "mocks",
            target_path=OAK_CLI_FLOPS_MOCKS_SLA_FOLDER_PATH,
        )


def copy_over_prepared_slas(
    prepared_slas_folder_path: pathlib.Path,
    target_path: pathlib.Path,
) -> None:
    for json_file in prepared_slas_folder_path.glob("*.json"):
        shutil.copy(json_file, target_path)


def get_sla_file_path(sla_folder: pathlib.Path, sla_file_name: Optional[str] = "") -> Path:
    if sla_file_name:
        sla_file_name = (
            sla_file_name if sla_file_name.endswith(".json") else sla_file_name + ".json"
        )
        sla_path = sla_folder / sla_file_name
        if not sla_path.is_file():
            logger.error(f"The SLA file '{sla_path}' does not exist.")
            sys.exit(1)
    else:
        relative_sla_file_path = prompt_for_path(
            "SLA File Name",
            promt_from_path=sla_folder,
            promt_subject="SLA name",
        )
        sla_path = sla_folder / relative_sla_file_path
    return sla_path
