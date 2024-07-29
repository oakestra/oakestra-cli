import enum
import pathlib

STAGE_FILE = pathlib.Path("/tmp/flops_stage")


class EvaluationRunFLOpsProjectStage(enum.Enum):
    EVALUATION_RUN_START = "Evaluation-Run Start"
    PROJECT_START = "Project Start"
    FL_ACTORS_IMAGE_BUIL = "FL-Actors Image Build"
    FL_TRAINING = "FL Training"
    START_POST_TRAINING_STEPS = "Start Post-Training Steps"
    TRAINED_MODEL_IMAGE_BUILD = "Trained-Model Image Build"
    DEPLOY_TRAINED_MODEL = "Deploy Trained-Model"


class EvaluationRunFLOpsCSVKeys(enum.Enum):
    STAGE = "Stage"
    # Time
    UNIX_TIMESTAMP = "UNIX Timestamp"
    TIME_SINCE_START = "Time Since Evaluation-Run Start"
    # Disk
    DISK_SPACE_CHANGE_SINCE_START = "Disk Space Change Since Start"
    DISK_SPACE_USED = "Disk Space Used"
    DISK_SPACE_CHANGE_SINCE_LAST_MEASUREMENT = "Disk Space Change Since Last Measurement"
    # CPU & Memory
    CPU_USAGE = "CPU Usage"
    MEMORY_USAGE = "Memory Usage"
    # Network
    NETWORK_RECEIVED_SINCE_START = "Network Received Since Start"
    NETWORK_SENT_SINCE_START = "Network Sent Since Start"
    NETWORK_RECEIVED_COMPARED_TO_LAST_MEASUREMENT = "Network Received Compared To Last Measurement"
    NETWORK_SENT_COMPARED_TO_LAST_MEASUREMENT = "Network Sent Compared To Last Measurement"


def handle_stage_file_at_evaluation_run_start() -> None:
    if not STAGE_FILE.exists():
        with open(STAGE_FILE, "w") as stage_file:
            stage_file.write(EvaluationRunFLOpsProjectStage.EVALUATION_RUN_START.value)


def get_current_stage() -> EvaluationRunFLOpsProjectStage:
    with open(STAGE_FILE, "r") as stage_file:
        return (
            EvaluationRunFLOpsProjectStage(stage_file.readline().replace("\n", ""))
            or EvaluationRunFLOpsProjectStage.EVALUATION_RUN_START
        )
