from oak_cli.commands.apps.main import get_applications
from oak_cli.utils.logging import logger


def display_current_applications() -> None:
    current_applications = get_applications()

    def log_aux(key: str, value: str) -> None:
        logger.debug(f"   {key}: '{value}'")

    logger.info(f"Current apps: '{len(current_applications)}'")
    for i, application in enumerate(current_applications):
        logger.info(f" App '{i}':")
        log_aux("id", application["applicationID"])
        log_aux("name", application["application_name"])
        log_aux("ns", application["application_namespace"])
        log_aux("desc", application["application_desc"])
        log_aux(
            "microservices",
            f"{len(application['microservices'])}: {application['microservices']}",
        )
