from typing import overload

from httpx import AsyncClient

from common.constants import DataSource
from common.datasources.arxiv import ArxivPaperDownloader
from common.datasources.base import PaperDownloader


class PaperDownloaderFactory:
    @overload
    @staticmethod
    def get(
        datasource_type: DataSource.ARXIV, client: AsyncClient
    ) -> ArxivPaperDownloader: ...

    @staticmethod
    def get(datasource_type: DataSource, client: AsyncClient) -> PaperDownloader:
        """Returns a paper downloader object based on the ingestion type.

        Args:
            datasource_type (DataSource): The ingestion to create base on datasource.
            client (AsyncClient): The httpx client to use for fetching paper metadata.

        Returns:
            PaperDownloader: The paper downloader object.

        Raises:
            KeyError: If the datasource_type type is unknown.
        """
        match datasource_type:
            case DataSource.ARXIV:
                return ArxivPaperDownloader(client)
            case _:
                raise KeyError(f"Unknown datasource type: {datasource_type}")
