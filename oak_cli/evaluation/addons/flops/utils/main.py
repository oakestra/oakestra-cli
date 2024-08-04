import enum

import pandas as pd
import seaborn as sns


class Evaluation(enum.Enum):
    SIMPLEST = 1

    SIMPLE_LARGE = 2
    SIMPLE_BASEIMAGES = 3
    SIMPLE_MULTIPLATFORM = 4

    SIMPLE_PYTORCH = 5
    SIMPLE_KERAS = 6

    BASEIMAGES_PART_TWO = 7

    SIMPLE_HFL = 8

    SIMPLE_MULTICLUSTER = 9
    SIMPLE_HFL_MULTICLUSTER = 10
    LARGER_HFL_MULTICLUSTER = 11


# Settings
VERBOSE = True


def _enforce_settings() -> None:
    if VERBOSE:
        pd.set_option("display.max_rows", None)
        pd.set_option("display.max_columns", None)

        import warnings

        warnings.simplefilter(action="ignore", category=FutureWarning)


def _set_styling() -> None:
    sns.set_style("whitegrid")


def prepare_notebook() -> None:
    _enforce_settings()
    _set_styling()
