PALETTE = "rainbow"
ROUNDING_PRECISION = 1  # Decimal places/digits


def get_evaluation_run_duration_label() -> str:
    return "Evaluation-Run Duration " + "(minutes)"


def adjust_xticks(ax) -> None:
    """Filters x-axis-ticks to include only whole numbers and multiples of 0.5"""
    current_ticks = ax.get_xticks()
    new_ticks = [tick for tick in current_ticks if round(tick * 2) == tick * 2]
    ax.set_xticks(new_ticks)
