from typing import overload

from httpx import AsyncClient

from common.constants import DataSource
from common.datasources.arxiv import ArxivCategoryFetcher
from uuid import UUID


class CategoryFetcherFactory:
    @overload
    @staticmethod
    def create(
        datasource_type: DataSource.ARXIV, datasource_uuid: UUID, client: AsyncClient
    ) -> ArxivCategoryFetcher: ...

    @staticmethod
    def create(datasource_type: DataSource, datasource_uuid: UUID, client: AsyncClient):
        """Creates a category fetcher object based on the ingestion type.

        Args:
            datasource_type (DataSource): The ingestion to create base on datasource.
            datasource_uuid (UUID): The uuid of the datasource.
            client (AsyncClient): The httpx client to use for fetching categories.

        Returns:
            CategoryFetcher: The category fetcher object.

        Raises:
            KeyError: If the datasource_type type is unknown.
        """
        if datasource_type == DataSource.ARXIV:
            return ArxivCategoryFetcher(client, datasource_uuid)
        raise KeyError(f"Unknown datasource type: {datasource_type}")
