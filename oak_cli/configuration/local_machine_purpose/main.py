import json
from typing import List, Optional, Set

from oak_cli.configuration.common import (
    check_and_handle_config_file,
    get_config_value,
    update_config_value,
)
from oak_cli.configuration.keys.enums import ConfigurableConfigKey
from oak_cli.configuration.local_machine_purpose.enum import LocalMachinePurpose
from oak_cli.utils.logging import logger


def set_local_machine_purposes(
    local_machine_purposes_set: Set[LocalMachinePurpose], verbose: bool = True
) -> None:
    if LocalMachinePurpose.EVERYTHING in local_machine_purposes_set:
        local_machine_purposes_set = {LocalMachinePurpose.EVERYTHING}
    if LocalMachinePurpose.INITIAL in local_machine_purposes_set:
        local_machine_purposes_set = {LocalMachinePurpose.INITIAL}
    check_and_handle_config_file()
    update_config_value(
        key=ConfigurableConfigKey.LOCAL_MACHINE_PURPOSE,
        value=json.dumps([purpose.value for purpose in local_machine_purposes_set]),
    )
    if verbose:
        purposes_txt = [purpose.value for purpose in local_machine_purposes_set]
        logger.info(f'The local-machine-purposes have been updated to: "{purposes_txt}"')


def get_local_machine_purposes_from_config(
    terminate_if_key_is_missing_from_conf: bool = True,
) -> Optional[List[LocalMachinePurpose]]:
    check_and_handle_config_file()
    config_json_string = get_config_value(
        ConfigurableConfigKey.LOCAL_MACHINE_PURPOSE,
        terminate_if_key_is_missing_from_conf,
    )
    if not config_json_string:
        return None
    config_list = json.loads(config_json_string)
    return [LocalMachinePurpose(purpose_name) for purpose_name in config_list]


def check_if_local_machine_has_required_purposes(
    required_purposes: List[LocalMachinePurpose],
    initial_purpose_support: bool = False,
) -> bool:
    local_machine_purposes = get_local_machine_purposes_from_config(
        terminate_if_key_is_missing_from_conf=False
    )

    if LocalMachinePurpose.INITIAL in required_purposes and len(required_purposes) > 1:
        logger.critical(
            "Initial Purpose should not be placed into required purposes together with others."
            " Please use the dedicated bool option for this."
        )

    if not local_machine_purposes:
        return False
    if LocalMachinePurpose.EVERYTHING in local_machine_purposes:
        return True

    if initial_purpose_support and LocalMachinePurpose.INITIAL in local_machine_purposes:
        return True

    return set(required_purposes).issubset(set(local_machine_purposes))
