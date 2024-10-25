import typer

from oak_cli.configuration.consts import OAK_CLI_SLA_FOLDER_PATH
from oak_cli.utils.logging import logger

app = typer.Typer()


@app.command("local-machine-purpose")
def explain_local_machine_purpose() -> None:
    logger.debug(
        "The OAK CLI includes various features.\n"
        "Such as:\n"
        "- Interacting with the Oakestra API\n"
        "- Creating & Managing Oakestra Applications & Services\n"
        "- Using Oakestra Automations (e.g. for an easier & faster Setup)\n"
        "- Interacting with Oakestra Addons\n"
        "- Developing & Debugging Oakestra\n"
        "\n"
        "These features depend on the concrete usecase and environment.\n"
        "Endusers and Developers require different commands.\n"
        "Local machines that host Oakestra orchestrator components and those that do not,"
        "require different sets of commands.\n"
        "\n"
        "To support these different usecases the OAK CLI"
        " uses the concept of local-machine-purposes.\n"
        "They can be configured by running:\n"
    )
    logger.info("> oak configuration local-machine-purpose")


@app.command("SLAs")
def explain_SLAs() -> None:
    logger.debug(
        "The computational components that Oakestra orchestrates are called services.\n"
        "Services are wrapped inside Applications.\n"
        "Applications can have different numbers of services"
        " with various numbers of service replicas/instances.\n"
        "Applications get created, whereas services get appended and or deployed.\n\n"
        "All services and apps are defined in the form of Service-Level Agreement (SLA) files.\n"
        "\n"
        "The OAK CLI comes with a set of default SLAs.\n"
        f"The SLAs are located in '{OAK_CLI_SLA_FOLDER_PATH}'.\n"
        "\n"
        "To add or create your own custom SLAs simply prepare new SLA files"
        " via your favorite editor or script of choice"
        f" and add them to '{OAK_CLI_SLA_FOLDER_PATH}'\n"
        "\n"
        "Run 'oak app sla' to display the available SLAs in a more readable way."
    )
