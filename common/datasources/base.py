# pragma: no cover
from abc import ABC, abstractmethod
from datetime import datetime
from typing import AsyncIterable, ClassVar

import httpx

from common.datasources.schema import BasePaperSchema, DomainSchema, SubjectSchema


class CategoryFetcher(ABC):
    TIMEOUT: int = 30

    DATASOURCE_NAME: ClassVar[str] = NotImplemented

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


class PaperMetadataFetcher(ABC):
    TIMEOUT: int = 30

    DATASOURCE_NAME: ClassVar[str] = NotImplemented

    def __init__(self, client: httpx.AsyncClient):
        """Initialize the category fetcher.

        Args:
            client: The httpx client to use for fetching categories.
        """
        self._client = client

    @abstractmethod
    async def fetch_paper_metadata(
        self,
        domain: DomainSchema,
        from_date: datetime,
        until_date: datetime,
        offset: int,
    ) -> AsyncIterable[BasePaperSchema]:
        """Return fetched paper metadata for domain."""
        raise NotImplementedError
