import argparse
import enum
from typing import Optional

import typer
from typing_extensions import Annotated


class CustomEnum(enum.Enum):
    def __str__(self) -> str:
        return self.value


class Verbosity(enum.Enum):
    SIMPLE = "simple"
    DETAILED = "detailed"
    EXHAUSTIVE = "exhaustive"


VERBOSITY_FLAG_TYPE = Annotated[Optional[Verbosity], typer.Option("-v")]

LIVE_VIEW_FLAG_TYPE = Annotated[
    bool,
    typer.Option("-l", help="Use dynamic Live-Display. (Exit view e.g. via 'Ctr+c')"),
]

Id = str
ServiceId = Id
ApplicationId = Id

Service = dict
Application = dict

SLA = dict
DbObject = dict

Subparsers = argparse._SubParsersAction
