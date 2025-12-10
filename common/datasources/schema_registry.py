from logging import getLogger
from threading import Lock
from typing import Dict, List, Type

from .schema import BasePaperSchema

logger = getLogger(__name__)


class DatasourceSchemas:
    _registry: Dict[str, Type[BasePaperSchema]] = {}
    _lock = Lock()

    @classmethod
    def register(cls, schema_cls: Type[BasePaperSchema]):
        """Registers a schema class with the datasource registry.

        Args:
            schema_cls (Type[BasePaperSchema]): The schema class to register.

        Notes:
            This method is thread-safe.
        """
        source_name = schema_cls.source_name.lower()
        if source_name not in cls._registry:
            with cls._lock:
                if source_name not in cls._registry:
                    cls._registry[source_name] = schema_cls
                    logger.debug("Registered schema", extra={"schema": source_name})

    @classmethod
    def get_schema(cls, source_name: str) -> Type[BasePaperSchema]:
        """Retrieves a schema class from the datasource registry.

        Args:
            source_name (str): The name of the datasource to retrieve the schema for.

        Returns:
            Type[BasePaperSchema]: The schema class associated with the
                given datasource name.

        Raises:
            ValueError: If the schema is not found in the registry.
        """
        source_name = source_name.lower()
        if source_name not in cls._registry:
            raise ValueError(f"Schema not found: {source_name}")
        logger.debug("Retrieved schema", extra={"schema": source_name})
        return cls._registry[source_name]

    @classmethod
    def list_schemas(cls) -> List[str]:
        """Returns a list of all registered datasource names.

        Returns:
            List[str]: A list of all registered datasource names.
        """
        return list(cls._registry.keys())
