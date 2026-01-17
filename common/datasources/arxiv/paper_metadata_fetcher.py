from datetime import datetime
from typing import AsyncIterable, ClassVar, List, Optional
import xml.etree.ElementTree as ET

from common.datasources.arxiv.schema import ArxivPaperSchema
from common.utils.logger.logger_config import LoggerManager

from ..base import PaperMetadataFetcher

logger = LoggerManager.get_logger(__name__)


class ArxivPaperMetadataFetcher(PaperMetadataFetcher[ArxivPaperSchema]):
    DATASOURCE_NAME: ClassVar[str] = "arxiv"

    BASE_URL: ClassVar[str] = "https://oaipmh.arxiv.org/oai"
    NAMESPACE = {
        "dc": "http://purl.org/dc/elements/1.1/",
        "oai": "http://www.openarchives.org/OAI/2.0/",
        "oai_dc": "http://www.openarchives.org/OAI/2.0/oai_dc/",
    }
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
    ) -> AsyncIterable[List[ArxivPaperSchema]]:
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
            resumption_token = self._get_resumption_token(response.text)
            records = self._parser_oai_response(
                response.text, subject_code, domain_code
            )
            yield records
            if not resumption_token:
                break

    def _get_resumption_token(self, xml_text: str) -> Optional[str]:
        """Extracts the resumption token from an arXiv API response XML.

        Args:
            xml_text (str): The XML text of the arXiv API response.

        Returns:
            Optional[str]: The resumption token if present, otherwise None.
        """
        resumption_token = None
        root = ET.fromstring(xml_text)
        token_el = root.find(".//oai:resumptionToken", self.NAMESPACE)
        if token_el is not None:
            resumption_token = token_el.text.strip()
        return resumption_token

    def _parser_oai_response(
        self, xml_text: str, primary_subject_code: str, domain_code: str
    ) -> List[ArxivPaperSchema]:
        """Parses an arXiv API response XML into a list of paper metadata objects.

        Args:
            xml_text (str): The XML text of the arXiv API response.
            primary_subject_code (str): The primary subject code of the record.
            domain_code (str): The domain code of the record.

        Returns:
            List[ArxivPaperSchema]: A list of paper metadata objects.
        """
        root = ET.fromstring(xml_text)

        records: List[ArxivPaperSchema] = []

        for record_el in root.findall(".//oai:record", self.NAMESPACE):
            try:
                header = record_el.find("oai:header", self.NAMESPACE)
                metadata = record_el.find("oai:metadata", self.NAMESPACE)

                if header is None or metadata is None:
                    continue
                arxiv_el = metadata.find("oai_dc:dc", self.NAMESPACE)
                if arxiv_el is None:
                    continue
                abstract = self._get_abstract(arxiv_el)
                arxiv_id = self._get_arxiv_id(header)
                authors = self._get_authors(arxiv_el)
                title = self._get_title(arxiv_el)
                subjects = self._get_subjects(header, primary_subject_code)
                publication_date = self._get_date(arxiv_el)
                records.append(
                    ArxivPaperSchema(
                        abstract=abstract,
                        arxiv_id=arxiv_id,
                        authors=authors,
                        domain=domain_code,
                        primary_subject=primary_subject_code,
                        publish_date=publication_date,
                        secondary_subjects=subjects,
                        title=title,
                    )
                )
            except Exception as e:
                logger.error("Parsing arXiv record failed", exc_info=e)

        return records

    def _get_subjects(self, header: ET.Element, primary_subject_code: str) -> List[str]:
        """Extracts all subjects from an arXiv API record header.

        Args:
            header (ET.Element): The header element of the arXiv API record.
            primary_subject_code (str): The primary subject code of the record.

        Returns:
            List[str]: A list of all subjects extracted from the record header.
        """
        subjects = []
        for set_el in header.findall("oai:setSpec", self.NAMESPACE):
            subject = set_el.text.strip().lower()
            if subject != primary_subject_code:
                subjects.append(subject)
        return subjects

    def _get_arxiv_id(self, header: ET.Element) -> str:
        """Extracts the arXiv ID from an arXiv API record element.

        Args:
            header (ET.Element): The head element .

        Returns:
            str: The arXiv ID of the record.
        """
        arxiv_id = header.find("oai:identifier", self.NAMESPACE).text.strip()
        arxiv_id = arxiv_id.rsplit(":", 1)[-1]
        return arxiv_id

    def _get_authors(self, arxiv_el: ET.Element) -> List[str]:
        """Extracts all authors from an arXiv API record element.

        Args:
            arxiv_el (ET.Element): The element of the arXiv API record.

        Returns:
            List[str]: A list of all authors extracted from the record element.
        """
        authors = []
        for author in arxiv_el.findall("dc:creator", self.NAMESPACE):
            authors.append(author.text.strip())
        return authors

    def _get_title(self, arxiv_el: ET.Element) -> str:
        """Extracts the title from an arXiv API record element.

        Args:
            arxiv_el (ET.Element): The element of the arXiv API record.

        Returns:
            str: The title of the record.
        """
        title = arxiv_el.find("dc:title", self.NAMESPACE).text.strip()
        return title

    def _get_abstract(self, arxiv_el: ET.Element) -> str:
        """Extracts the abstract from an arXiv API record element.

        Args:
            arxiv_el (ET.Element): The element of the arXiv API record.

        Returns:
            str: The abstract of the record.
        """
        abstract = arxiv_el.find("dc:description", self.NAMESPACE).text.strip()
        return abstract

    def _get_date(self, arxiv_el: ET.Element) -> str:
        """Extracts the date from an arXiv API record element.

        Args:
            arxiv_el (ET.Element): The element of the arXiv API record.

        Returns:
            str: The date of the record.
        """
        date = arxiv_el.findall("dc:date", self.NAMESPACE)
        return date[-1].text.strip()
