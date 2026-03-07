import asyncio
from datetime import datetime
from typing import AsyncIterator, ClassVar

from common.datasources.arxiv.const import DATASOURCE_NAME
from common.datasources.arxiv.schema import ArxivPaperMetadataRecord
from common.datasources.base import PaperMetadataFetcher
from common.utils.logger.logger_config import LoggerManager

logger = LoggerManager.get_logger(__name__)


class ArxivPaperMetadataFetcher(PaperMetadataFetcher[ArxivPaperMetadataRecord]):
    DATASOURCE_NAME: ClassVar[str] = DATASOURCE_NAME

    BASE_URL: ClassVar[str] = "https://export.arxiv.org/api/query"

    @staticmethod
    def _get_request_parameters(
        subject_code: str,
        from_date: datetime,
        until_date: datetime,
        start_index: int,
    ):
        start_date = from_date.strftime("%Y%m%d%H%M")
        end_date = until_date.strftime("%Y%m%d%H%M")
        date_range = f"[{start_date} TO {end_date}]"

        params = {}
        params["search_query"] = f"cat:{subject_code} AND submittedDate:{date_range}"
        params["sortBy"] = "submittedDate"
        params["sortOrder"] = "ascending"
        params["start"] = start_index
        params["max_results"] = "1000"
        return params

    async def _request(self, url: str, params: dict) -> str:
        """Requests a URL with given parameters and timeout.

        Args:
            url (str): The URL to request.
            params (dict): The request parameters as a dictionary.

        Returns:
            str: The response text.

        Raises:
            Exception: If all retries fail.
        """
        await asyncio.sleep(3)
        logger.debug(f"Requesting {url} with params {params}")
        response = await self._client.get(url, params=params, timeout=self.TIMEOUT)
        response.raise_for_status()
        return response.text if response.text != "" else None

    async def fetch_paper_metadata(
        self,
        domain_code: str,
        subject_code: str,
        from_date: datetime,
        until_date: datetime,
    ) -> AsyncIterator[ArxivPaperMetadataRecord]:
        """Fetches paper metadata from the arXiv API.

        Args:
            domain_code (str): The domain code to query.
            subject_code (str): The subject code to query.
            from_date (datetime): The from date to query.
            until_date (datetime): The until date to query.

        Yields:
            AsyncIterator[ArxivPaperSchema]: An asynchronous iterator
                of paper metadata objects.
        """
        logger.debug(
            "Start fetching paper metadata", extra={"subject_code": subject_code}
        )

        start_index = 0
        raw_data = ""
        total_fetched = 0
        while raw_data is not None:
            params = self._get_request_parameters(
                subject_code, from_date, until_date, start_index
            )
            raw_data = await self._request(self.BASE_URL, params)
            if raw_data is None:
                break

            records = self._paper_parser.parse(raw_data, domain_code)
            for record in records:
                start_index += 1
                total_fetched += 1
                logger.debug(
                    "Total Fetched paper metadata",
                    extra={
                        "domain_code": domain_code,
                        "subject_code": subject_code,
                        "total_fetched": total_fetched,
                    },
                )
                yield record

        logger.debug(
            "Finished fetching paper metadata", extra={"subject_code": subject_code}
        )
