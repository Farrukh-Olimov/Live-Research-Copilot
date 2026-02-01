from typing import ClassVar

from common.datasources.arxiv.const import DATASOURCE_NAME
from common.datasources.arxiv.schema import ArxivPaperMetadataRecord
from common.datasources.base import PaperMetadataNormalizer
from common.datasources.schema import PaperMetadataRecord


class ArxivPaperMetadataNormalize(PaperMetadataNormalizer[ArxivPaperMetadataRecord]):
    DATASOURCE_NAME: ClassVar[str] = DATASOURCE_NAME

    def normalize(self, paper_record: ArxivPaperMetadataRecord) -> PaperMetadataRecord:
        """Normalizes an arXiv paper metadata object into a PaperMetadataRecord.

        Args:
            paper_record (ArxivPaperMetadataRecord): The arXiv paper metadata
                object to normalize.

        Returns:
            PaperMetadataRecord: The normalized paper metadata object.
        """
        return PaperMetadataRecord(
            abstract=paper_record.abstract,
            authors=paper_record.authors,
            domain_code=paper_record.domain_code,
            paper_id=paper_record.arxiv_id,
            primary_subject_code=paper_record.primary_subject_code,
            publish_date=paper_record.publish_date,
            secondary_subject_codes=paper_record.secondary_subject_codes,
            source=ArxivPaperMetadataRecord.DATASOURCE_NAME,
            title=paper_record.title,
        )
