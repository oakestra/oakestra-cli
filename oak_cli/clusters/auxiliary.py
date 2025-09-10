import string
from rich.table import Table

from oak_cli.clusters.common import get_clusters
from oak_cli.utils.styling import (
    OAK_GREEN,
    add_column,
    add_plain_columns,
    add_row_to_table,
    create_table,
)
from oak_cli.utils.types import Verbosity

cluster_info_to_column_name_map = {
    "Location": "cluster_location",
    "Active Nodes": "active_nodes",
    "Virtualizations": "virtualization",
    "CPU% Utilization": "aggregated_cpu_percent",
    "Available Memory": "memory_in_mb",
    "Last update": "last_modified_timestamp",
    "IP Address": "ip",
    "Port": "port",
    "Total vCPU": "total_cpu_cores",
    "Total vGPUs": "total_gpu_cores",
    "Supported Addons": "supported_addons",
}


def generate_current_cluster_table(live: bool, all: bool) -> Table:
    table = create_table(
        caption="Current Clusters",
        live=live,
    )
    add_column(table, column_name="Name", style=OAK_GREEN)
    add_plain_columns(table=table, column_names=["Location", "Active Nodes", "Virtualizations"])
    if all:
        add_plain_columns(table=table, column_names=["Status"])

    current_clusters = get_clusters(all=all)
    if not current_clusters:
        return table

    for cluster in current_clusters:
        special_row_items = []
        if all:
            if cluster["active"]:
                special_row_items += ["Connected 🟢"]
            else:
                special_row_items += ["Disconnected 🔴"]

        row_items = [
            cluster["cluster_name"],
            cluster["cluster_location"],
            str(cluster["active_nodes"]),
            str(cluster["virtualization"]),
        ] + special_row_items
        add_row_to_table(table=table, row_items=row_items)

    return table


def generate_cluster_detail_table(live: bool, name: string) -> Table:
    table = create_table(
        caption=f"Cluster [{name}] Details",
        live=live,
    )
    add_column(table, column_name=f"Cluster Name", style=OAK_GREEN)
    add_plain_columns(table=table, column_names=[f"{name}"])

    current_clusters = get_clusters(all=all)
    if not current_clusters:
        return table

    for cluster in current_clusters:
        if cluster["cluster_name"] != name:
            continue

        for key, column_name in cluster_info_to_column_name_map.items():
            add_row_to_table(table=table, row_items=[key, str(cluster[column_name])])

        if cluster["active"]:
            add_row_to_table(table=table, row_items=["Status", "Connected 🟢"])
        else:
            add_row_to_table(table=table, row_items=["Status", "Disconnected 🔴"])

    return table
