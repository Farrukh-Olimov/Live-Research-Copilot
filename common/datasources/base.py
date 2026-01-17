# pragma: no cover
from abc import ABC, abstractmethod
from datetime import datetime
from typing import AsyncIterable, ClassVar, Dict, Generic, TypeVar

import httpx

from common.datasources.schema import BasePaperSchema, DomainSchema, SubjectSchema

PaperSchemaT = TypeVar("PaperSchemaT", bound=BasePaperSchema)


class CategoryFetcher(ABC):
    TIMEOUT: int = 30

    DATASOURCE_NAME: ClassVar[str]

    def __init__(self, client: httpx.AsyncClient):
        """Initialize the category fetcher.

        Args:
            client: The httpx client to use for fetching categories.
        """
        self._client = client

    @abstractmethod
    async def fetch_subjects(self) -> AsyncIterable[SubjectSchema]:
        """Return all subjects supported by the datasource."""
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def _parse_set(
        set_spec: str, set_name: str, domains: Dict[str, DomainSchema]
    ) -> SubjectSchema:
        """Parse a single set specification into a SubjectSchema object."""
        raise NotImplementedError


class PaperMetadataFetcher(Generic[PaperSchemaT], ABC):
    TIMEOUT: int = 30

    DATASOURCE_NAME: ClassVar[str]

    def __init__(self, client: httpx.AsyncClient):
        """Initialize the category fetcher.

        Args:
            client: The httpx client to use for fetching categories.
        """
        self._client = client

    @abstractmethod
    async def fetch_paper_metadata(
        self,
        subject_code: str,
        from_date: datetime,
        until_date: datetime,
    ) -> AsyncIterable[PaperSchemaT]:
        """Fetches paper metadata from the datasource.

        Args:
            subject_code (str): The subject code to query.
            from_date (datetime): The from date to query.
            until_date (datetime): The until date to query.

        Returns:
            AsyncIterable[PaperSchemaT]: An asynchronous iterable
                of paper metadata objects.
        """
        pass
