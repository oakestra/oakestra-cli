import rich
import typer
from icecream import ic

from oak_cli.utils.typer_augmentations import AliasGroup
from oak_cli.utils.types import Service, Verbosity

ic.configureOutput(prefix="")
app = typer.Typer(cls=AliasGroup)


def display_single_service(
    service: Service,
    verbosity: Verbosity = Verbosity.SIMPLE.value,
) -> None:
    if verbosity == Verbosity.EXHAUSTIVE:
        for i, instance in enumerate(service["instance_list"]):
            instance["cpu_history"] = "..."
            instance["memory_history"] = "..."
            instance["logs"] = "..."
            ic(i, service)

    table = rich.table.Table(
        caption=f"Current Applications (verbosity: '{verbosity.value}')",
        box=rich.box.ROUNDED,
        show_lines=True,
    )
    # match verbosity:
    #     case Verbosity.SIMPLE:
    #         name = service["microservice_name"]
    #         instances = len(service["instance_list"])
    #         ic(name, instance)
    #         return
    #     case Verbosity.EXHAUSTIVE:
    #         for instance in service["instance_list"]:
    #             instance["cpu_history"] = "..."
    #             instance["memory_history"] = "..."
    #             instance["logs"] = "..."
    #             ic(service)
    #     case Verbosity.DETAILED:
    #         mask = [
    #             "addresses",
    #             "app_name",
    #             "app_ns",
    #             "applicationID",
    #             "service_name",
    #             "service_ns",
    #             "service_ns",
    #             "one_shot",
    #             "microserviceID",
    #             "cmd",
    #             "code",
    #             "image",
    #         ]
    #         service = {key: service[key] for key in mask if key in service}

    # ic(service)
