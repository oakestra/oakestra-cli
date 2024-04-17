from icecream import ic

from oak_cli.commands.apps.main import get_applications

ic.configureOutput(prefix="")


def display_current_applications() -> None:
    current_applications = get_applications()
    for i, application in enumerate(current_applications):
        ic(i, application)
