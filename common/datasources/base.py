from abc import ABC, abstractmethod
from typing import AsyncIterable

import httpx

from common.datasources.schema import SubjectSchema


class CategoryFetcher(ABC):
    TIMEOUT: int = 30

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
