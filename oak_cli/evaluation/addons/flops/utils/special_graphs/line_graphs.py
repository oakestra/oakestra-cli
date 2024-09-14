import pandas as pd
import seaborn as sns

from oak_cli.evaluation.addons.flops.utils.draw import draw_graph
from oak_cli.evaluation.addons.flops.utils.keys import (
    CPU_KEY,
    DISK_START_KEY,
    MEMORY_KEY,
    NETWORK_START_KEYS,
    NETWORK_START_RECEIVED_KEY,
    NETWORK_START_SENT_KEY,
    NODE_KEY,
    RUN_ID_KEY,
    STAGE_KEY,
    TIME_START_KEY,
)


def draw_cpu_and_memory_linegraph(
    normalized_data: pd.DataFrame,
) -> None:
    data_keys = [CPU_KEY, MEMORY_KEY, STAGE_KEY]
    draw_graph(
        title="Evaluation Runs Average",
        data=normalized_data[data_keys + [RUN_ID_KEY]],
        plot_functions=[lambda: sns.lineplot(data=normalized_data[data_keys])],
        use_percentage_limits=True,
        y_label="Resource Usage (%)",
        show_stages=True,
        use_median_stages=True,
    )


def draw_cpu_linegraph(
    normalized_data: pd.DataFrame,
    multi_cluster: bool = False,
) -> None:
    data_keys = [CPU_KEY, STAGE_KEY]
    if multi_cluster:
        data_keys.append(NODE_KEY)
    draw_graph(
        title="Evaluation Runs Average",
        data=normalized_data[data_keys + [RUN_ID_KEY]],
        plot_functions=[
            lambda: sns.lineplot(
                x=TIME_START_KEY,
                y=CPU_KEY,
                data=normalized_data[data_keys],
                hue=NODE_KEY if multi_cluster else None,
            )
        ],
        use_percentage_limits=True,
        y_label="CPU Usage (%)",
        show_stages=True,
        use_median_stages=True,
    )


def draw_memory_linegraph(
    normalized_data: pd.DataFrame,
    multi_cluster: bool = False,
) -> None:
    data_keys = [MEMORY_KEY, STAGE_KEY]
    if multi_cluster:
        data_keys.append(NODE_KEY)
    draw_graph(
        title="Evaluation Runs Average",
        data=normalized_data[data_keys + [RUN_ID_KEY]],
        plot_functions=[
            lambda: sns.lineplot(
                x=TIME_START_KEY,
                y=MEMORY_KEY,
                data=normalized_data[data_keys],
                hue=NODE_KEY if multi_cluster else None,
            )
        ],
        use_percentage_limits=True,
        y_label="Memory Usage (%)",
        show_stages=True,
        use_median_stages=True,
    )


def draw_disk_space_linegraph(
    normalized_data: pd.DataFrame,
    multi_cluster: bool = False,
) -> None:
    data_keys = [DISK_START_KEY, STAGE_KEY]
    if multi_cluster:
        data_keys.append(NODE_KEY)

    _normalized_df = normalized_data.copy()
    _normalized_df[[DISK_START_KEY]] = _normalized_df[[DISK_START_KEY]] / 1024
    draw_graph(
        title="Evaluation Runs Average",
        data=_normalized_df[data_keys + [RUN_ID_KEY]],
        plot_functions=[
            lambda: sns.lineplot(
                x=TIME_START_KEY,
                y=DISK_START_KEY,
                data=_normalized_df[data_keys],
                hue=NODE_KEY if multi_cluster else None,
            )
        ],
        y_label="Disk Space Change (GB)",
        x_lim=(0, max(_normalized_df.index)),
        y_lim=0,
        show_stages=True,
        use_median_stages=True,
    )


def draw_network_linegraph(normalized_data: pd.DataFrame) -> None:
    _normalized_df = normalized_data.copy()
    _normalized_df[NETWORK_START_KEYS] = _normalized_df[NETWORK_START_KEYS] / 1024
    draw_graph(
        title="Evaluation Runs Average",
        data=_normalized_df[NETWORK_START_KEYS + [STAGE_KEY, RUN_ID_KEY]],
        plot_functions=[
            lambda: sns.lineplot(data=_normalized_df[NETWORK_START_KEYS + [STAGE_KEY]])
        ],
        y_label="Network Change (I/O) (GB)",
        x_lim=(0, max(_normalized_df.index)),
        y_lim=0,
        show_stages=True,
        use_median_stages=True,
    )


def draw_network_received_linegraph(
    normalized_data: pd.DataFrame,
    multi_cluster: bool = False,
) -> None:
    data_keys = [NETWORK_START_RECEIVED_KEY, STAGE_KEY]
    if multi_cluster:
        data_keys.append(NODE_KEY)

    _normalized_df = normalized_data.copy()
    _normalized_df[[NETWORK_START_RECEIVED_KEY]] = (
        _normalized_df[[NETWORK_START_RECEIVED_KEY]] / 1024
    )
    draw_graph(
        title="Evaluation Runs Average",
        data=_normalized_df[data_keys + [RUN_ID_KEY]],
        plot_functions=[
            lambda: sns.lineplot(
                x=TIME_START_KEY,
                y=NETWORK_START_RECEIVED_KEY,
                data=_normalized_df[data_keys],
                hue=NODE_KEY if multi_cluster else None,
            )
        ],
        y_label="Network Received (GB)",
        x_lim=(0, max(_normalized_df.index)),
        y_lim=0,
        show_stages=True,
        use_median_stages=True,
    )


def draw_network_send_linegraph(
    normalized_data: pd.DataFrame,
    multi_cluster: bool = False,
) -> None:
    data_keys = [NETWORK_START_SENT_KEY, STAGE_KEY]
    if multi_cluster:
        data_keys.append(NODE_KEY)

    _normalized_df = normalized_data.copy()
    _normalized_df[[NETWORK_START_SENT_KEY]] = _normalized_df[[NETWORK_START_SENT_KEY]] / 1024
    draw_graph(
        title="Evaluation Runs Average",
        data=_normalized_df[data_keys + [RUN_ID_KEY]],
        plot_functions=[
            lambda: sns.lineplot(
                x=TIME_START_KEY,
                y=NETWORK_START_SENT_KEY,
                data=_normalized_df[data_keys],
                hue=NODE_KEY if multi_cluster else None,
            )
        ],
        y_label="Network Sent (GB)",
        x_lim=(0, max(_normalized_df.index)),
        y_lim=0,
        show_stages=True,
        use_median_stages=True,
    )
