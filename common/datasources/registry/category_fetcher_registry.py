from logging import getLogger
from threading import Lock
from typing import Dict, List, Type

from ..base import CategoryFetcher

logger = getLogger(__name__)


class CategoryFetcherRegistry:
    _registry: Dict[str, Type[CategoryFetcher]] = {}
    _lock: Lock = Lock()

    @classmethod
    def get_schema(cls, datasource_name: str) -> Type[CategoryFetcher]:
        """Retrieves a schema class from the datasource registry.

        Args:
            datasource_name (str): The name of the datasource to retrieve the
                schema for.

        Returns:
            Type[CategoryFetcher]: The category fetcher class associated with the
              given datasource name.

        Raises:
            KeyError: If the schema is not found in the registry.
        """
        datasource_name = datasource_name.lower()
        if datasource_name not in cls._registry:
            raise KeyError(f"Schema not found: {datasource_name}")
        logger.debug("Retrieved schema", extra={"schema": datasource_name})
        return cls._registry[datasource_name]

    @classmethod
    def list_schemas(cls) -> List[str]:
        """Returns a list of all registered datasource names.

        Returns:
            List[str]: A list of all registered datasource names.
        """
        return list(cls._registry.keys())

    @classmethod
    def register(cls, schema_cls: Type[CategoryFetcher]):
        """Registers a schema class with the datasource registry.

        Args:
            schema_cls (Type[BasePaperSchema]): The category fetcher class to register.

        Notes:
            This method is thread-safe.
        """
        datasource_name = schema_cls.DATASOURCE_NAME.lower()
        if datasource_name not in cls._registry:
            with cls._lock:
                if datasource_name not in cls._registry:  # pragma: no cover
                    cls._registry[datasource_name] = schema_cls
                    logger.debug("Registered schema", extra={"schema": datasource_name})
        return schema_cls

    @classmethod
    def unregister(cls, datasource_name: str):
        """Unregisters a schema class from the datasource registry.

        Args:
            datasource_name (str): The name of the datasource to unregister.

        Raises:
            KeyError: If the schema is not found in the registry.
        """
        if datasource_name in cls._registry:
            with cls._lock:
                cls._registry.pop(datasource_name)
        else:
            raise KeyError(f"Schema not found: {datasource_name}") from None

    @classmethod
    def clear(cls):
        """Clears the datasource registry."""
        with cls._lock:
            cls._registry.clear()
