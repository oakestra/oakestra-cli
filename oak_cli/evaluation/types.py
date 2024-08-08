import enum
from abc import abstractmethod
from typing import Any, ClassVar, List

from pydantic import BaseModel


class EvaluationScenario(enum.Enum):
    RESOURCES = "Resources"
    FLOPS_MONOLITH = "FLOps-Monolith"
    FLOPS_MULTI_CLUSTER = "FLOps-multi-cluster"


class CSVKeys(str, enum.Enum):
    pass


class MetricsManager(BaseModel):
    scenario: ClassVar[EvaluationScenario]

    @abstractmethod
    def create_csv_header(self) -> List[str]:
        pass

    @abstractmethod
    def create_csv_line_entries() -> List[Any]:
        pass
