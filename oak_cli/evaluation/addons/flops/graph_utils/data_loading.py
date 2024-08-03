import glob
import pathlib

import pandas as pd

import enum

class MachineSetup(enum.Enum):
    MONOLITH = "monolith"
    CHAIR_VM_TRIPLET = "chair vm triplet"

class Dataset(enum.Enum):
    MNIST = "MNIST"
    CIFAR10 = "CIFAR10"

class Framework(enum.Enum):
    SKLEARN = "sklearn"
    PYTORCH = "pytorch"
    KERAS = "keras"

class ProjectSize(enum.Enum):
    SMALL = "small"
    LARGE = "large"

def load_data(machine_setup: MachineSetup = MachineSetup.MONOLITH,
              dataset: Dataset = Dataset.MNIST,
              framework: Framework = Framework.SKLEARN,
              project_size: ProjectSize = ProjectSize.SMALL,
              use_baseimages: bool = False,
              use_multiplatform: bool = False,
              ) -> pd.DataFrame:
    

csvs_root = pathlib.Path(__file__).parents[1] / "csvs"

# csv_dir = get_csv_dir_for_scenario(EvaluationScenario.FLOPS)
csv_dir = csvs_root / "monolith_mnist_sklearn_small_without_baseimages"

csv_files = glob.glob(f"{csv_dir}/evaluation_run_*.csv")
df = pd.concat([pd.read_csv(file) for file in csv_files], ignore_index=True)

# Add a numerical stage ID (instead of the string) for future numerical manipulations.
df[STAGE_ID_KEY] = df[STAGE_KEY].apply(
    lambda stage_name: EvaluationRunFLOpsProjectStage(stage_name).get_index()
)

# trained_model_df = pd.read_csv(TRAINED_MODEL_PERFORMANCE_CSV)
trained_model_df = pd.read_csv(csv_dir / "trained_models.csv")

# NOTE: The CSV "time-since-start" values are very precise, thus they differ (slightly) between Evaluation-Runs.
# This difference leads to issues when trying to plot them in an aggregated way.
# To fix this we cast the floats to ints instead. I.e. we are looking at whole seconds - which is fine for this concrete use-case.
df[[TIME_START_KEY]] = round(df[[TIME_START_KEY]].astype(int) / 60, ROUNDING_PRECISION)

df.set_index(TIME_START_KEY, inplace=True)

normalized_df = normalize_df_time_ranges(df)

singular_run_df = df[df[RUN_ID_KEY] == (df[RUN_ID_KEY].max() // 2)]
