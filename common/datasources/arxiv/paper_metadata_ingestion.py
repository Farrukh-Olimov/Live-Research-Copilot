from datetime import datetime
from typing import AsyncIterator, ClassVar

from httpx import AsyncClient

from common.datasources.arxiv.const import DATASOURCE_NAME
from common.datasources.arxiv.paper_metadata_fetcher import ArxivPaperMetadataFetcher
from common.datasources.arxiv.paper_metadata_parser import ArxivPaperMetadataParser
from common.datasources.arxiv.paper_normalizer import ArxivPaperMetadataNormalize
from common.datasources.arxiv.schema import ArxivPaperMetadataRecord
from common.datasources.base import PaperMetadataIngestion, PaperMetadataRecord
from common.utils.logger.logger_config import LoggerManager

logger = LoggerManager.get_logger(__name__)


class ArxivPaperMetadataIngestion(PaperMetadataIngestion[ArxivPaperMetadataRecord]):
    DATASOURCE_NAME: ClassVar[str] = DATASOURCE_NAME

    def __init__(self, client: AsyncClient):
        """Initializes an ArxivPaperMetadataIngestion object.

        Args:
            client (AsyncClient): The httpx client to use for fetching paper metadata.
        """
        parser = ArxivPaperMetadataParser()
        normalizer = ArxivPaperMetadataNormalize()
        fetcher = ArxivPaperMetadataFetcher(client, parser)
        super().__init__(fetcher, normalizer)

    async def run(
        self, subject: str, from_date: datetime, until_date: datetime
    ) -> AsyncIterator[PaperMetadataRecord]:
        """Runs the paper metadata ingestion for a given subject and date range.

        Args:
            subject (str): The subject to ingest.
            from_date (datetime): The from date to ingest.
            until_date (datetime): The until date to ingest.

        Yields:
            AsyncIterator[PaperMetadataRecord]: An asynchronous iterator
                of paper metadata records.
        """
        logger.info(
            "Start ingesting paper metadata",
            extra={
                "subject": subject,
                "from_date": from_date,
                "until_date": until_date,
            },
        )

        async for paper in self._fetcher.fetch_paper_metadata(
            subject, from_date, until_date
        ):
            normalized_paper_metadata = self._normalizer.normalize(paper)
            yield normalized_paper_metadata

        logger.info(
            "Finished ingesting paper metadata",
            extra={
                "subject": subject,
                "from_date": from_date,
                "until_date": until_date,
            },
        )
