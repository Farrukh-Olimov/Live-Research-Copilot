from typing import List, Optional
import xml.etree.ElementTree as ET

from common.datasources.arxiv.const import NAMESPACE
from common.datasources.arxiv.schema import ArxivPaperMetadataRecord
from common.utils.logger.logger_config import LoggerManager

logger = LoggerManager.get_logger(__name__)


class ArxivPaperParser:
    def parse(
        self, raw_data: str, primary_subject_code: str, domain_code: str
    ) -> List[ArxivPaperMetadataRecord]:
        """Parses an arXiv API response XML into a list of paper metadata objects.

        Args:
            raw_data (str): The XML text of the arXiv API response.
            primary_subject_code (str): The primary subject code of the record.
            domain_code (str): The domain code of the record.

        Returns:
            List[ArxivPaperSchema]: A list of paper metadata objects.
        """
        root = ET.fromstring(raw_data)
        records: List[ArxivPaperMetadataRecord] = []

        for record_el in root.findall(".//oai:record", NAMESPACE):
            try:
                header = record_el.find("oai:header", NAMESPACE)
                metadata = record_el.find("oai:metadata", NAMESPACE)

                if header is None or metadata is None:
                    continue

                arxiv_el = metadata.find("oai_dc:dc", NAMESPACE)
                if arxiv_el is None:
                    continue

                abstract = self._get_abstract(arxiv_el)
                arxiv_id = self._get_arxiv_id(header)
                authors = self._get_authors(arxiv_el)
                title = self._get_title(arxiv_el)
                subjects = self._get_subjects(header, primary_subject_code)
                publication_date = self._get_date(arxiv_el)
                records.append(
                    ArxivPaperMetadataRecord(
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
        for set_el in header.findall("oai:setSpec", NAMESPACE):
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
        arxiv_id = header.find("oai:identifier", NAMESPACE).text.strip()
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
        for author in arxiv_el.findall("dc:creator", NAMESPACE):
            authors.append(author.text.strip())
        return authors

    def _get_title(self, arxiv_el: ET.Element) -> str:
        """Extracts the title from an arXiv API record element.

        Args:
            arxiv_el (ET.Element): The element of the arXiv API record.

        Returns:
            str: The title of the record.
        """
        title = arxiv_el.find("dc:title", NAMESPACE).text.strip()
        return title

    def _get_abstract(self, arxiv_el: ET.Element) -> str:
        """Extracts the abstract from an arXiv API record element.

        Args:
            arxiv_el (ET.Element): The element of the arXiv API record.

        Returns:
            str: The abstract of the record.
        """
        abstract = arxiv_el.find("dc:description", NAMESPACE).text.strip()
        return abstract

    def _get_date(self, arxiv_el: ET.Element) -> str:
        """Extracts the date from an arXiv API record element.

        Args:
            arxiv_el (ET.Element): The element of the arXiv API record.

        Returns:
            str: The date of the record.
        """
        date = arxiv_el.findall("dc:date", NAMESPACE)
        return date[-1].text.strip()

    def get_resumption_token(self, raw_data: str) -> Optional[str]:
        """Extracts the resumption token from an arXiv API response XML.

        Args:
            raw_data (str): The XML text of the arXiv API response.

        Returns:
            Optional[str]: The resumption token if present, otherwise None.
        """
        resumption_token = None
        root = ET.fromstring(raw_data)
        token_el = root.find(".//oai:resumptionToken", NAMESPACE)
        if token_el is not None:
            resumption_token = token_el.text.strip()
        return resumption_token
