from datetime import date, datetime
from typing import ClassVar, List
import xml.etree.ElementTree as ET

from common.datasources.arxiv.const import DATASOURCE_NAME, PAPER_NAMESPACE
from common.datasources.arxiv.schema import ArxivPaperMetadataRecord
from common.datasources.base import PaperMetadataParser
from common.utils.logger import LoggerManager

logger = LoggerManager.get_logger(__name__)


class ArxivPaperMetadataParser(PaperMetadataParser[ArxivPaperMetadataRecord]):
    DATASOURCE_NAME: ClassVar[str] = DATASOURCE_NAME

    def parse(self, raw_data: str, domain_code: str) -> List[ArxivPaperMetadataRecord]:
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

        for record_el in root.findall("atom:entry", PAPER_NAMESPACE):
            try:
                abstract = self._get_abstract(record_el)
                arxiv_id = self._get_arxiv_id(record_el)
                authors = self._get_authors(record_el)
                title = self._get_title(record_el)
                primary_subject_code = self._get_primary_category(record_el)
                subject_codes = self._get_subject_codes(record_el, primary_subject_code)
                publication_date = self._get_publication_date(record_el)
                records.append(
                    ArxivPaperMetadataRecord(
                        abstract=abstract,
                        arxiv_id=arxiv_id,
                        authors=authors,
                        domain_code=domain_code,
                        primary_subject_code=primary_subject_code,
                        publish_date=publication_date,
                        secondary_subject_codes=subject_codes,
                        title=title,
                    )
                )
            except Exception as e:
                logger.error("Parsing arXiv record failed", exc_info=e)

        return records

    def _get_subject_codes(
        self, header: ET.Element, primary_subject_code: str
    ) -> List[str]:
        """Extracts all subjects from an arXiv API record header.

        Args:
            header (ET.Element): The header element of the arXiv API record.
            primary_subject_code (str): The primary subject code of the record.

        Returns:
            List[str]: A list of all subjects extracted from the record header.
        """
        subjects = []
        for set_el in header.findall("atom:category", PAPER_NAMESPACE):
            subject = set_el.attrib["term"]
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
        arxiv_id = header.find("atom:id", PAPER_NAMESPACE).text.strip()
        arxiv_id = arxiv_id.rsplit("/", 1)[-1]
        return arxiv_id

    def _get_authors(self, arxiv_el: ET.Element) -> List[str]:
        """Extracts all authors from an arXiv API record element.

        Args:
            arxiv_el (ET.Element): The element of the arXiv API record.

        Returns:
            List[str]: A list of all authors extracted from the record element.
        """
        authors = []
        for author in arxiv_el.findall("atom:author", PAPER_NAMESPACE):
            name = author.find("atom:name", PAPER_NAMESPACE).text
            authors.append(name.strip())
        return authors

    def _get_title(self, arxiv_el: ET.Element) -> str:
        """Extracts the title from an arXiv API record element.

        Args:
            arxiv_el (ET.Element): The element of the arXiv API record.

        Returns:
            str: The title of the record.
        """
        title = arxiv_el.find("atom:title", PAPER_NAMESPACE).text.strip()
        return title

    def _get_abstract(self, arxiv_el: ET.Element) -> str:
        """Extracts the abstract from an arXiv API record element.

        Args:
            arxiv_el (ET.Element): The element of the arXiv API record.

        Returns:
            str: The abstract of the record.
        """
        abstract = arxiv_el.find("atom:summary", PAPER_NAMESPACE).text.strip()
        return abstract

    def _get_publication_date(self, arxiv_el: ET.Element) -> date:
        """Extracts the date from an arXiv API record element.

        Actually, it is last modified date of the paper.

        Args:
            arxiv_el (ET.Element): The element of the arXiv API record.

        Returns:
            date: The date of the record.
        """
        paper_date = arxiv_el.find("atom:published", PAPER_NAMESPACE)
        paper_date = paper_date.text.strip()
        return datetime.fromisoformat(paper_date).date()

    def _get_primary_category(self, arxiv_el: ET.Element) -> str:
        """Extracts the primary category from an arXiv API record element.

        Args:
            arxiv_el (ET.Element): The element of the arXiv API record.

        Returns:
            str: The primary category of the record.
        """
        return arxiv_el.find("arxiv:primary_category", PAPER_NAMESPACE).attrib["term"]
