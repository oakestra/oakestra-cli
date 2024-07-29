import enum
import pathlib
from typing import Any, List

from oak_cli.evaluation.resources.main import ResourcesMetricManager
from oak_cli.evaluation.types import CSVKeys, EvaluationScenario

STAGE_FILE = pathlib.Path("/tmp/flops_stage")


class EvaluationRunFLOpsProjectStage(enum.Enum):
    EVALUATION_RUN_START = "Evaluation-Run Start"
    PROJECT_START = "Project Start"
    FL_ACTORS_IMAGE_BUIL = "FL-Actors Image Build"
    FL_TRAINING = "FL Training"
    START_POST_TRAINING_STEPS = "Start Post-Training Steps"
    TRAINED_MODEL_IMAGE_BUILD = "Trained-Model Image Build"
    DEPLOY_TRAINED_MODEL = "Deploy Trained-Model"


class FLOpsExclusiveCSVKeys(CSVKeys):
    """NOTE: The FLOPs Evaluation CSV also includes the same CSV keys as the ResourcesCSV
    (AFAIK) it is not trivially possible to extend Enums.
    Thus they need to be carefully combined/handled.
    """

    FLOPS_PROJECT_STAGE = "FLOps Project Stage"


def handle_stage_file_at_evaluation_run_start() -> None:
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
        return [key.value for key in FLOpsExclusiveCSVKeys] + super().create_csv_header()

    def create_csv_line_entries(self) -> List[Any]:
        return [get_current_stage().value] + super().create_csv_line_entries()
