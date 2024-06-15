# NOTE:
# This code is intended to be viewed as a somewhat working example of good to have features.
# Currently this code features a first draft implementation of showing CPU (and Memory) usage Graphs
# next to the logs in the terminal.
# I can confirm that this is in deed feasable and the following combination makes this possible:
# - "Rich" tables (https://rich.readthedocs.io/en/stable/tables.html)
# - https://pypi.org/project/asciichartpy/
# This code was intended to be part of the "inspect_service" method and the intended use was:
# The CLI user could inspect a service and see in the "instances" table next to the logs,
# the graphs of the resource usage.
# asciichartpy is capable of displaying multiple graphs in one graph with different colors.
# -> Thus I think there should not be screen-space issues,
# especially if we scale the graph via asciichartpy or trim the values accordingly.
# I repeat - it works to show this resource data via a graph in the terminal as part of a cell
# in a "rich" table.
# Have a look at layouts (https://rich.readthedocs.io/en/stable/layout.html#layout)
# they could be great for this, (or be a nightmare like CSS ...).


# NOTE: COMMENTED OUT to avoid any possible linter issues, etc.

# import datetime

# import asciichartpy
# import typer

# from oak_cli.services.auxiliary import add_icon_to_status
# from oak_cli.services.common import get_single_service
# from oak_cli.utils.styling import (
#     OAK_GREEN,
#     OAK_WHITE,
#     add_column,
#     add_plain_columns,
#     create_table,
#     print_table,
# )
# from oak_cli.utils.typer_augmentations import AliasGroup
# from oak_cli.utils.types import ServiceId

# app = typer.Typer(cls=AliasGroup)


# # @app.command("inspect, i", help="Inspect the specified service.")
# def inspect_service(service_id: ServiceId) -> None:
#     service = get_single_service(service_id=service_id)
#     instances = service["instance_list"]
#     caption = "" if instances else "No instances deployed"
#     service_table = create_table(caption=caption)
#     add_column(service_table, column_name="Service Name", style=OAK_GREEN)
#     add_column(service_table, column_name="Service Status", style=OAK_WHITE)
#     add_plain_columns(service_table, column_names=["App Name", "App ID", "Image", "Command"])
#     service_status = service.get("status")
#     service_table.add_row(
#         service["microservice_name"],
#         add_icon_to_status(service_status) if service_status else "-",
#         service["app_name"],
#         service["applicationID"],
#         service["image"],
#         " ".join(service["cmd"]) if service["cmd"] else "-",
#     )
#     print_table(service_table)
#     if not instances:
#         return

#     instances_table = create_table(title="Instances")
#     add_column(instances_table, "#", style=OAK_GREEN)
#     add_column(instances_table, "Logs")
#     add_column(instances_table, "CPU Usage")
#     for instance in instances:

#         data = instance["cpu_history"]
#         # Convert timestamps to datetime objects for easier manipulation
#         timestamps = [
#             datetime.datetime.strptime(ts["timestamp"], "%Y-%m-%dT%H:%M:%S.%f") for ts in data
#         ]
#         values = [float(ts["value"]) for ts in data]
#         # Ensure both lists have the same length
#         assert len(timestamps) == len(
#             values
#         ), "Timestamps and values lists must have the same length"
#         # Sort the data by timestamp.
#         sorted_data = sorted(zip(timestamps, values), key=lambda x: x[0])
#         # Extract just the timestamps and values for plotting.
#         sorted_timestamps, sorted_values = zip(*sorted_data)

#         # table = create_table(caption="testing")
#         # add_column(table, column_name="chart test", style="blue")
#         # table.add_row(asciichartpy.plot(sorted_values))
#         # print_table(table)

#         # config = {
#         #     "colors": [
#         #         asciichartpy.blue
#         #         # asciichartpy.green,
#         #         # asciichartpy.default,
#         #     ]
#         # }

#         config = {"min": 0, "color": [asciichartpy.blue]}

#         row_elements = [
#             str(instance.get("instance_number")),
#             instance.get("logs"),
#             # str(instance.get("cpu_history")),
#             # asciichartpy.plot([sorted_values], config),
#             asciichartpy.plot(series=sorted_values, cfg=config),
#         ]
#         instances_table.add_row(*row_elements)
#     print_table(instances_table)
