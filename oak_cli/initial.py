from oak_cli.configuration.consts import OAK_CLI_USER_FOLDER_PATH
from oak_cli.utils.ascii.main import print_welcome_logo

_INIT_FILE_PATH = OAK_CLI_USER_FOLDER_PATH / ".init_flag"


def handle_init_use() -> None:
    if not _is_init_use():
        return

    _INIT_FILE_PATH.touch()
    print_welcome_logo()


def _is_init_use() -> bool:
    return not _INIT_FILE_PATH.exists()
