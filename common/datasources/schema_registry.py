from threading import Lock
from typing import Dict, Type

from .schema import BasePaperSchema


class DatasourceSchemas:
    _registry = Dict[str, Type[BasePaperSchema]] = {}
    _lock = Lock()

    @classmethod
    def register(cls, schema_cls: Type[BasePaperSchema]):
        if schema_cls.source_name not in cls._registry:
            with cls._lock:
                if schema_cls.source_name not in cls._registry:
                    cls._registry[schema_cls.source_name] = schema_cls
