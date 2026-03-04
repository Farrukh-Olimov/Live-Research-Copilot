from typing import overload

from httpx import AsyncClient

from common.constants import DataSource
from common.datasources.arxiv import ArxivPaperMetadataIngestion
from common.datasources.base import PaperMetadataIngestion


class PaperMetadataIngestionFactory:

    @overload
    @staticmethod
    def get(
        datasource_type: DataSource.ARXIV, client: AsyncClient
    ) -> ArxivPaperMetadataIngestion: ...

    @staticmethod
    def get(datasource_type: DataSource, client: AsyncClient) -> PaperMetadataIngestion:
        """Creates a paper metadata ingestion object based on the ingestion type.

        Args:
            datasource_type (DataSource): The ingestion to create base on datasource.
            client (AsyncClient): The httpx client to use for fetching paper metadata.

        Returns:
            PaperMetadataIngestion: The paper metadata ingestion object.

        Raises:
            KeyError: If the datasource_type type is unknown.
        """
        match datasource_type:
            case DataSource.ARXIV:
                return ArxivPaperMetadataIngestion(client)
            case _:
                raise KeyError(f"Unknown datasource type: {datasource_type}")
