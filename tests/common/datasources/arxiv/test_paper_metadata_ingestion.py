from datetime import datetime

import pytest

from common.datasources.arxiv import ArxivPaperMetadataIngestion
from common.datasources.base import PaperMetadataRecord


@pytest.mark.asyncio
async def test_arxiv_paper_metadata_ingestion(httpx_async_client):
    """Tests that the ArxivPaperMetadataIngestion can fetch paper metadata records."""
    arxiv_ingestion = ArxivPaperMetadataIngestion(client=httpx_async_client)
    papers = []
    async for paper in arxiv_ingestion.run(
        subject="cs", from_date=datetime(2022, 1, 1), until_date=datetime(2022, 1, 1)
    ):
        assert isinstance(
            paper, PaperMetadataRecord
        ), f"Expected PaperMetadataRecord, got {type(paper)}"
        papers.append(paper)

    assert len(papers) > 1, "Expected at least two papers"
