import pytest

from common.constants import DataSource
from common.datasources.arxiv import ArxivPaperMetadataIngestion
from common.datasources.factories import PaperMetadataIngestionFactory


def test_paper_metadata_ingestion_factory_error():
    """Tests that the PaperMetadataIngestionFactory raises a KeyError."""
    with pytest.raises(KeyError):
        PaperMetadataIngestionFactory.get("NoValue", None)


def test_paper_metadata_ingestion_factory():
    """Tests the PaperMetadataIngestionFactory creates the correct ingestion type."""
    ingestion = PaperMetadataIngestionFactory.get(DataSource.ARXIV, None)
    assert isinstance(ingestion, ArxivPaperMetadataIngestion)
