from typing import List


def add_icon_to_status(status: str) -> str:
    STATUS_ICON_MAP = {
        "RUNNING": "🟢",
        "ACTIVE": "❇️",
        "NODE_SCHEDULED": "🔵",
        "NoActiveClusterWithCapacity": "❌",
    }
    return f"{status} {STATUS_ICON_MAP.get(status, '❓')}"


def show_instances(instances: List[dict]) -> str:
    instance_status_info = []
    for i in instances:
        info = f"{i['instance_number']}:{add_icon_to_status(i['status'])}"
        instance_status_info.append(info)

    resulting_string = f"({len(instances)})"
    if len(instance_status_info) > 0:
        resulting_string += f" - {instance_status_info}"
    return resulting_string
