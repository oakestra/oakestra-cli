import enum
import pathlib
from typing import Any, List

from oak_cli.evaluation.resources.main import ResourcesMetricManager
from oak_cli.evaluation.types import CSVKeys, EvaluationScenario

STAGE_FILE = pathlib.Path("/tmp/flops_stage")
TRAINED_MODEL_PERFORMANCE_CSV = pathlib.Path("/tmp/flops_trained_models.csv")


class EvaluationRunFLOpsProjectStage(enum.Enum):
    EVALUATION_RUN_START = "Evaluation-Run Start"
    PROJECT_START = "Project Start"
    FL_ACTORS_IMAGE_BUIL = "FL-Actors Image Build"
    FL_TRAINING = "FL Training"
    START_POST_TRAINING_STEPS = "Start Post-Training Steps"
    TRAINED_MODEL_IMAGE_BUILD = "Trained-Model Image Build"
    DEPLOY_TRAINED_MODEL = "Deploy Trained-Model"


# NOTE: One could also turn the enum values above into tuples.
# E.g. PROJECT_START = "Project Start", 1
# To avoid confusion we use a dedicated map instead.
FLOPS_STAGES_INDEX_MAP = {
    EvaluationRunFLOpsProjectStage.EVALUATION_RUN_START: 0,
    EvaluationRunFLOpsProjectStage.PROJECT_START: 1,
    EvaluationRunFLOpsProjectStage.FL_ACTORS_IMAGE_BUIL: 2,
    EvaluationRunFLOpsProjectStage.FL_TRAINING: 3,
    EvaluationRunFLOpsProjectStage.START_POST_TRAINING_STEPS: 4,
    EvaluationRunFLOpsProjectStage.TRAINED_MODEL_IMAGE_BUILD: 5,
    EvaluationRunFLOpsProjectStage.DEPLOY_TRAINED_MODEL: 6,
}


class FLOpsExclusiveCSVKeys(CSVKeys):
    """NOTE: The FLOPs Evaluation CSV also includes the same CSV keys as the ResourcesCSV
    (AFAIK) it is not trivially possible to extend Enums.
    Thus they need to be carefully combined/handled.
    """

    FLOPS_PROJECT_STAGE = "FLOps Project Stage"


class FLOpsTrainedModelCSVKeys(CSVKeys):
    EVALUATION_RUN = "Evaluation-Run"
    ACCURACY = "Accuracy"
    LOSS = "Loss"


def handle_flops_files_at_evaluation_run_start() -> None:
    if not STAGE_FILE.exists():
        with open(STAGE_FILE, "w") as stage_file:
            stage_file.write(EvaluationRunFLOpsProjectStage.EVALUATION_RUN_START.value)


def get_current_stage() -> EvaluationRunFLOpsProjectStage:
    with open(STAGE_FILE, "r") as stage_file:
        return EvaluationRunFLOpsProjectStage(
            stage_file.readline().replace("\n", "")
            or EvaluationRunFLOpsProjectStage.EVALUATION_RUN_START.value
        )


class FLOpsMetricManager(ResourcesMetricManager):
    scenario = EvaluationScenario.FLOPS

    def create_csv_header(self) -> List[str]:
        return super().create_csv_header() + [key.value for key in FLOpsExclusiveCSVKeys]

    def create_csv_line_entries(self) -> List[Any]:
        return super().create_csv_line_entries() + [get_current_stage().value]
