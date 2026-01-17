from datetime import datetime
from typing import AsyncIterable, ClassVar, List, Optional

from common.datasources.arxiv.const import DATASOURCE_NAME
from common.datasources.arxiv.schema import ArxivPaperMetadataRecord
from common.datasources.base import PaperMetadataFetcher
from common.utils.logger.logger_config import LoggerManager

logger = LoggerManager.get_logger(__name__)


class ArxivPaperMetadataFetcher(PaperMetadataFetcher[ArxivPaperMetadataRecord]):
    DATASOURCE_NAME: ClassVar[str] = DATASOURCE_NAME

    BASE_URL: ClassVar[str] = "https://oaipmh.arxiv.org/oai"

    PARAMS = {"verb": "ListRecords"}

    @staticmethod
    def get_request_parameters(
        subject_code: str,
        from_data: datetime,
        until_data: datetime,
        resumption_token: Optional[str],
    ):
        """Construct request parameters for the arXiv API.

        Args:
            subject_code (str): The subject code to query.
            from_data (datetime): The from date to query.
            until_data (datetime): The until date to query.
            resumption_token (Optional[str]): The resumption token to query.

        Returns:
            Dict[str, str]: The request parameters as a dictionary.
        """
        params = ArxivPaperMetadataFetcher.PARAMS.copy()
        if resumption_token:
            params["resumptionToken"] = resumption_token
        else:
            params["metadataPrefix"] = "oai_dc"
            params["from"] = from_data.strftime("%Y-%m-%d")
            params["until"] = until_data.strftime("%Y-%m-%d")
            params["set"] = subject_code
        return params

    async def fetch_paper_metadata(
        self,
        subject_code: str,
        from_date: datetime,
        until_date: datetime,
    ) -> AsyncIterable[List[ArxivPaperMetadataRecord]]:
        """Fetches paper metadata from the arXiv API.

        Args:
            subject_code (str): The subject code to query.
            from_date (datetime): The from date to query.
            until_date (datetime): The until date to query.

        Yields:
            AsyncIterable[ArxivPaperSchema]: An asynchronous iterable
                of paper metadata objects.
        """
        resumption_token = None
        domain_code = subject_code.split(":")[0]

        while True:
            params = self.get_request_parameters(
                subject_code, from_date, until_date, resumption_token
            )

            response = await self._client.get(
                self.BASE_URL, params=params, timeout=self.TIMEOUT
            )
            response.raise_for_status()
            resumption_token = self._paper_parser.get_resumption_token(response.text)
            records = self._paper_parser.parse(response.text, subject_code, domain_code)
            yield records
            if not resumption_token:
                break
