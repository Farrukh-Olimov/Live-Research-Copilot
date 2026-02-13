from datetime import datetime

from httpx import AsyncClient
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from common.constants import DataSource
from common.database.postgres.models import Author, Datasource, Domain, Subject
from common.database.postgres.repositories import DatabaseRepository
from common.datasources.factories import (
    CategoryFetcherFactory,
    PaperMetadataIngestionFactory,
)
from common.datasources.schema import PaperMetadataRecord
from common.services.ingestion import (
    CategoryIngestionService,
    PaperMetadataIngestionService,
)


@pytest.mark.asyncio
class TestPaperMetadataIngestionService:
    """Unit tests for PaperMetadataIngestionService helpers."""

    @pytest.fixture(autouse=True)
    def _setup(
        self,
        httpx_async_client: AsyncClient,
        async_session_factory: async_sessionmaker[AsyncSession],
    ):
        """Shared service + repository wiring per test."""
        self._async_session_factory = async_session_factory
        self._http_client = httpx_async_client

        self.factory = PaperMetadataIngestionFactory()
        self._database = DatabaseRepository()

        self.ingest_service = PaperMetadataIngestionService(
            factory=self.factory,
            database_repository=self._database,
            db_session_factory=async_session_factory,
            http_client=httpx_async_client,
        )

    async def test_get_datasource_uuid(self):
        """Test the datasource uuid lookup."""
        async with self._async_session_factory() as session:
            with pytest.raises(ValueError):
                await self.ingest_service._get_datasource_uuid(
                    DataSource.ARXIV, session
                )

            creaed_datasource = await self._database.datasource.create(
                Datasource(name=DataSource.ARXIV),
                session,
            )
            uuid = await self.ingest_service._get_datasource_uuid(
                DataSource.ARXIV, session
            )
            assert uuid == creaed_datasource.id, "UUID does not match"

    async def test_get_domain(self):
        """Test the domain lookup."""
        async with self._async_session_factory() as session:
            datasource = await self._database.datasource.create(
                Datasource(name=DataSource.ARXIV),
                session,
            )
            domain = await self.ingest_service._get_domain(
                "cs",
                datasource.id,
                DataSource.ARXIV,
                session,
            )
            assert domain is None, "Domain should not be found"

            created_domain = await self._database.domain.create(
                Domain(
                    code="cs",
                    name="Computer Science",
                    datasource_id=datasource.id,
                ),
                session,
            )
            domain = await self.ingest_service._get_domain(
                "cs",
                datasource.id,
                DataSource.ARXIV,
                session,
            )
            assert domain is not None, "Domain should be found"
            assert domain.id == created_domain.id, "Domain ID does not match"
            assert domain.code == created_domain.code, "Domain code does not match"

    async def test_get_subject(self):
        """Test the subject lookup."""
        async with self._async_session_factory() as session:
            datasource = await self._database.datasource.create(
                Datasource(name=DataSource.ARXIV),
                session,
            )

            subject = await self.ingest_service._get_subject(
                "cs.AI", datasource.id, DataSource.ARXIV, session
            )
            assert subject is None, "Subject should not be found"

            created_domain = await self._database.domain.create(
                Domain(
                    code="cs",
                    name="Computer Science",
                    datasource_id=datasource.id,
                ),
                session,
            )
            created_subject = await self._database.subject.create(
                Subject(
                    code="cs.AI",
                    name="Artificial Intelligence",
                    domain_id=created_domain.id,
                ),
                session,
            )
            subject = await self.ingest_service._get_subject(
                "cs.AI", datasource.id, DataSource.ARXIV, session
            )
            assert subject is not None, "Subject should be found"
            assert subject.id == created_subject.id, "Subject ID does not match"
            assert subject.code == created_subject.code, "Subject code does not match"

    async def test_get_or_create_authors(self):
        """Test the list of authors."""
        async with self._async_session_factory() as session:
            datasource = await self._database.datasource.create(
                Datasource(name=DataSource.ARXIV),
                session,
            )
            paper_authors = ["John Doe", "Jane Doe"]
            authors = await self.ingest_service._get_or_create_authors(
                paper_authors,
                datasource.id,
                DataSource.ARXIV,
                session,
            )
            assert all(
                [isinstance(author, Author) for author in authors]
            ), "All authors should be instances"
            assert len(authors) == 2, "Expected 2 authors"
            assert authors[0].name == "John Doe", "Author name does not match"
            assert authors[1].name == "Jane Doe", "Author name does not match"

        # test if aauthor in db already
        async with self._async_session_factory() as session:
            author = await self._database.author.create(
                Author(name=paper_authors[0]), session
            )
            authors = await self.ingest_service._get_or_create_authors(
                paper_authors,
                datasource.id,
                DataSource.ARXIV,
                session,
            )
            assert author == authors[0], "Author does not match"

    async def test_ingest_one(self):
        """Test the ingest one method."""
        async with self._async_session_factory() as session:
            datasource = await self._database.datasource.create(
                Datasource(name=DataSource.ARXIV),
                session,
            )

            paper = PaperMetadataRecord(
                abstract="Testing abstract",
                authors=["John Doe", "Jane Doe"],
                domain_code="cs",
                paper_id="123",
                primary_subject_code="cs.AI",
                publish_date="2022-01-01",
                secondary_subject_codes=["cs.LG"],
                source="arXiv",
                title="Test Paper",
            )
            created_paper = await self.ingest_service._ingest_one(
                paper,
                datasource.id,
                DataSource.ARXIV,
                session,
            )
            assert created_paper is None, "Paper should not be ingested"

            created_domain = await self._database.domain.create(
                Domain(
                    code="cs",
                    name="Computer Science",
                    datasource_id=datasource.id,
                ),
                session,
            )
            await self._database.subject.create(
                Subject(
                    code="cs.AI",
                    name="Artificial Intelligence",
                    domain_id=created_domain.id,
                ),
                session,
            )
            created_paper = await self.ingest_service._ingest_one(
                paper,
                datasource.id,
                DataSource.ARXIV,
                session,
            )
            assert created_paper is not None, "Paper should be ingested"
            assert created_paper.abstract == paper.abstract, "Abstract does not match"
            assert created_paper.domain == created_domain, "Domain code does not match"
            assert (
                created_paper.paper_identifier == paper.paper_id
            ), "Paper ID does not match"
            assert (
                created_paper.publish_date == paper.publish_date
            ), "Publish date does not match"
            assert created_paper.title == paper.title, "Title does not match"

            subject_codes = []
            subject_codes.append(paper.primary_subject_code)
            subject_codes.extend(paper.secondary_subject_codes)

            for i, ps in enumerate(created_paper.paper_subjects):
                await session.refresh(ps, attribute_names=["subject"])
                assert (
                    ps.subject.code == subject_codes[i]
                ), "Subject name does not match"

    async def test_run(self):
        """Test the run method."""
        async with self._async_session_factory() as session:
            datasource = await self._database.datasource.create(
                Datasource(name=DataSource.ARXIV),
                session,
            )
            await session.commit()

        category_fetcher = CategoryFetcherFactory.create(
            DataSource.ARXIV, datasource.id, self._http_client
        )
        category_ingestion = CategoryIngestionService(self._async_session_factory)
        async for subject in category_fetcher.fetch_subjects():
            await category_ingestion.ingest_subject(subject)

        fromTime = datetime(2022, 1, 1)
        untilTime = datetime(2022, 1, 1)
        await self.ingest_service.run(
            DataSource.ARXIV,
            subject.code,
            fromTime,
            untilTime,
        )

        async with self._async_session_factory() as session:
            created_papers_number = await self._database.paper.count_papers(
                datasource_id=datasource.id, session=session
            )
            assert created_papers_number > 0, "Expected at least one paper"
