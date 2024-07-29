import enum
from abc import abstractmethod
from typing import Any, ClassVar, List

from pydantic import BaseModel


class EvaluationScenario(enum.Enum):
    RESOURCES = "Resources"
    FLOPS = "FLOps"


class CSVKeys(str, enum.Enum):
    pass


class MetricsManager(BaseModel):
    scenario: ClassVar[EvaluationScenario]
    csv_keys: ClassVar[CSVKeys.__class__]

    def create_csv_header(self) -> List[str]:
        return [key.value for key in self.csv_keys]  # type: ignore

    @abstractmethod
    def create_csv_line_entries() -> List[Any]:
        pass
