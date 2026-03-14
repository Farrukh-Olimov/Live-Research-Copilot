from typing import ClassVar
from urllib.parse import urljoin

from common.datasources.arxiv.const import DATASOURCE_NAME
from common.datasources.base import PaperDownloader
from common.utils.logger.logger_config import LoggerManager

logger = LoggerManager.get_logger(__name__)


class ArxivPaperDownloader(PaperDownloader):
    DATASOURCE_NAME: ClassVar[str] = DATASOURCE_NAME

    # sensitive to / at the end of the url
    BASE_URL: ClassVar[str] = "https://arxiv.org/pdf/"

    async def _request(self, url: str) -> bytes:
        """Requests a URL with the given parameters and timeout.

        Args:
            url (str): The URL to request.

        Returns:
            bytes: The response content.

        Raises:
            Exception: If all retries fail.
        """
        logger.debug(f"Requesting {url}")
        response = await self._client.get(url, timeout=self.TIMEOUT)
        response.raise_for_status()
        return response.content

    async def download(self, paper_identifier: str) -> bytes:
        """Downloads the paper with the given identifier from arXiv.

        Args:
            paper_identifier (str): The identifier of the paper to download.

        Returns:
            bytes: The content of the downloaded paper.

        Raises:
            Exception: If all retries fail.
        """
        url = urljoin(self.BASE_URL, paper_identifier)
        return await self._request(url)
