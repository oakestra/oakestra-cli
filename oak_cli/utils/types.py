import argparse
import enum


class CustomEnum(enum.Enum):
    def __str__(self) -> str:
        return self.value


# class Verbosity(enum.Enum):
class Verbosity(enum.Enum):
    SIMPLE = "simple"
    DETAILED = "detailed"
    EXHAUSTIVE = "exhaustive"


Id = str
ServiceId = Id
ApplicationId = Id

Service = dict
Application = dict

SLA = dict
DbObject = dict

Subparsers = argparse._SubParsersAction
