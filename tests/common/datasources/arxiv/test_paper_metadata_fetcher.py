from datetime import datetime

import pytest

from common.datasources.arxiv import ArxivPaperMetadataFetcher, ArxivPaperMetadataParser


@pytest.mark.asyncio
async def test_arxiv_paper_metadata_fetcher(httpx_async_client):
    """Tests single page fetching using the ArxivPaperMetadataFetcher."""
    fromTime = datetime(2022, 1, 1)
    untilTime = datetime(2022, 1, 1)

    fetcher = ArxivPaperMetadataFetcher(
        client=httpx_async_client, paper_parser=ArxivPaperMetadataParser()
    )

    records = []
    async for record in fetcher.fetch_paper_metadata(
        domain_code="cs.cs",
        subject_code="cs.AI",
        from_date=fromTime,
        until_date=untilTime,
    ):
        records.append(record)
        break
    assert len(records) > 0, "Expected at least one record"
