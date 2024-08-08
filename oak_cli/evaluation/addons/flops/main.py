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
    FL_ACTORS_IMAGE_BUILDER_DEPLOYMENT = "FL-Actors Image-Builder Deployment"
    FL_ACTORS_IMAGE_BUILD = "FL-Actors Image Build"
    AGGREGATOR_DEPLOYMENT = "Aggregator Deployment"
    FL_TRAINING = "FL Training"
    START_POST_TRAINING_STEPS = "Start Post-Training Steps"
    TRAINED_MODEL_IMAGE_BUILDER_DEPLOYMENT = "Trained-Model Image-Builder Deployment"
    TRAINED_MODEL_IMAGE_BUILD = "Trained-Model Image Build"
    DEPLOY_TRAINED_MODEL = "Deploy Trained-Model"

    def get_index(self) -> int:
        return list(self.__class__).index(self)


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


class FLOpsMetricManagerMonolith(ResourcesMetricManager):
    scenario = EvaluationScenario.FLOPS_MONOLITH

    def create_csv_header(self) -> List[str]:
        return super().create_csv_header() + [key.value for key in FLOpsExclusiveCSVKeys]

    def create_csv_line_entries(self) -> List[Any]:
        return super().create_csv_line_entries() + [get_current_stage().value]


class FLOpsMetricManagerMultiCluster(ResourcesMetricManager):
    scenario = EvaluationScenario.FLOPS_MULTI_CLUSTER

    def create_csv_header(self) -> List[str]:
        return super().create_csv_header() + [key.value for key in FLOpsExclusiveCSVKeys]

    def create_csv_line_entries(self) -> List[Any]:
        return super().create_csv_line_entries() + [get_current_stage().value]
