from abc import ABC
from typing import ClassVar


class BasePaperSchema(ABC):
    source_name: ClassVar[str]
