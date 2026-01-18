from datetime import datetime
from typing import List

import pytest

from common.datasources.arxiv import ArxivPaperMetadataFetcher, ArxivPaperParser
from common.datasources.arxiv.schema import ArxivPaperMetadataRecord


@pytest.mark.asyncio
async def test_arxiv_paper_metadata_fetcher(httpx_async_client):
    """Tests single page fetching using the ArxivPaperMetadataFetcher."""
    fromTime = datetime(2022, 1, 1)
    untilTime = datetime(2022, 1, 1)

    fetcher = ArxivPaperMetadataFetcher(
        client=httpx_async_client, paper_parser=ArxivPaperParser()
    )

    records = []
    async for record in fetcher.fetch_paper_metadata(
        subject_code="cs", from_date=fromTime, until_date=untilTime
    ):
        records.append(record)
        break
    assert len(records) > 0, "Expected at least one record"


@pytest.mark.asyncio
async def test_arxiv_paper_metadata_fetcher_resumptionToken(httpx_async_client):
    """Test resumptionToken for ArxivPaperMetadataFetcher."""
    fromTime = datetime(2022, 1, 1)
    untilTime = datetime(2022, 1, 1)

    fetcher = ArxivPaperMetadataFetcher(
        client=httpx_async_client, paper_parser=ArxivPaperParser()
    )
    all_records: List[ArxivPaperMetadataRecord] = []
    total_fetched = 0
    async for record in fetcher.fetch_paper_metadata(
        subject_code="cs", from_date=fromTime, until_date=untilTime
    ):
        assert record is not None, "Expected a record"
        all_records.append(record)
        total_fetched += 1

    assert len(all_records) > 1, "Expected at least two records"

    seen = set()
    for record in all_records:
        assert record.arxiv_id not in seen, "Expected unique arXiv IDs"
        seen.add(record.arxiv_id)
