from oak_cli.evaluation.localhost_resources.common import EvaluationRunCSVKeys

CPU_AND_MEMORY_KEYS = [
    EvaluationRunCSVKeys.CPU_USAGE.value,
    EvaluationRunCSVKeys.MEMORY_USAGE.value,
]


def get_evaluation_run_duration_label(use_minutes: bool = True) -> str:
    return "Evaluation-Run Duration " + "(minutes)" if use_minutes else "(seconds)"


def adjust_xticks(ax) -> None:
    """Filters x-axis-ticks to include only whole numbers and multiples of 0.5"""
    current_ticks = ax.get_xticks()
    new_ticks = [tick for tick in current_ticks if round(tick * 2) == tick * 2]
    ax.set_xticks(new_ticks)
