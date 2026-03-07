from uuid import uuid4

import pytest

from common.datasources.arxiv import ArxivSubjectsFetcher
from common.datasources.schema import SubjectSchema


@pytest.mark.asyncio
async def test_arxiv_fetch_subjects(httpx_async_client):
    """Tests that the ArxivCategoryFetcher can fetch subjects from the Arxiv API.

    This test uses the httpx_async_client fixture to mock out the HTTP requests
    to the Arxiv API. It then uses the ArxivCategoryFetcher to fetch subjects
    and asserts that the returned subjects are of type SubjectSchema and
    that at least one subject is returned.
    """
    fetcher = ArxivSubjectsFetcher(client=httpx_async_client, datasource_uuid=uuid4())
    counter = 0
    async for subject in fetcher.fetch_subjects():
        assert isinstance(
            subject, SubjectSchema
        ), f"Expected SubjectSchema, got {type(subject)}"
        counter += 1
    assert counter > 0, "Expected at least one subject"


def test_arxiv_parse_domain(httpx_async_client):
    """Tests that the ArxivCategoryFetcher parsing.

    This test uses the _parse_set method of the ArxivCategoryFetcher
    to parse a subject from arXiv into a SubjectSchema object.
    It then asserts that the returned subject is not None and that
    the subject code, name, and domain are as expected.
    It also asserts that the domain is cached in the domains dictionary.
    """
    domains = {}
    fetcher = ArxivSubjectsFetcher(client=httpx_async_client, datasource_uuid=uuid4())
    fetcher._parse_set("cs:cs", "Computer Science", domains)

    assert (
        len(domains) == 1 and domains["cs.cs"].code == "cs.cs"
    ), "Expected domain code to be 'cs'"

    subject = fetcher._parse_set("cs:cs:ai", "Artificial Intelligence", domains)

    assert subject is not None, "Expected subject to be parsed"
    assert subject.code == "cs.AI", "Expected subject code to be 'cs.AI'"
    assert (
        subject.name == "Artificial Intelligence"
    ), "Expected subject name to be 'Artificial Intelligence'"
    assert subject.domain.code == "cs.cs", "Expected domain code to be 'cs.cs'"
    assert (
        subject.domain.name == "Computer Science"
    ), "Expected domain name to be 'Computer Science'"
    assert subject.domain is domains["cs.cs"], "Expected domain to be cached"
