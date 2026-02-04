import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from common.constants import DataSource
from common.database.postgres.models import Author, Datasource, Domain, Subject
from common.database.postgres.repositories import (
    AuthorRespotitory,
    DatasourceRepository,
    DomainRepository,
    PaperRepository,
    SubjectRepository,
)
from common.datasources.factories import PaperMetadataIngestionFactory
from common.services.ingestion import PaperMetadataIngestionService


@pytest.mark.asyncio
class TestPaperMetadataIngestionService:
    """Unit tests for PaperMetadataIngestionService helpers."""

    @pytest.fixture(autouse=True)
    def _setup(
        self,
        async_session_factory: async_sessionmaker[AsyncSession],
    ):
        """Shared service + repository wiring per test."""
        self.async_session_factory = async_session_factory

        self.factory = PaperMetadataIngestionFactory()
        self.author_repo = AuthorRespotitory()
        self.datasource_repo = DatasourceRepository()
        self.domain_repo = DomainRepository()
        self.paper_repo = PaperRepository()
        self.subject_repo = SubjectRepository()

        self.service = PaperMetadataIngestionService(
            factory=self.factory,
            author_repository=self.author_repo,
            datasource_repository=self.datasource_repo,
            domain_repository=self.domain_repo,
            paper_repository=self.paper_repo,
            subject_repository=self.subject_repo,
            db_session_factory=async_session_factory,
            http_client=None,
        )

    async def test_get_datasource_uuid(self):
        """Test the datasource uuid lookup."""
        async with self.async_session_factory() as session:
            with pytest.raises(ValueError):
                await self.service._get_datasource_uuid(DataSource.ARXIV, session)

            creaed_datasource = await self.datasource_repo.create(
                Datasource(name=DataSource.ARXIV),
                session,
            )
            uuid = await self.service._get_datasource_uuid(DataSource.ARXIV, session)
            assert uuid == creaed_datasource.id, "UUID does not match"

    async def test_get_domain(self):
        """Test the domain lookup."""
        async with self.async_session_factory() as session:
            datasource = await self.datasource_repo.create(
                Datasource(name=DataSource.ARXIV),
                session,
            )
            domain = await self.service._get_domain(
                "cs",
                datasource.id,
                DataSource.ARXIV,
                session,
            )
            assert domain is None, "Domain should not be found"

            created_domain = await self.domain_repo.create(
                Domain(
                    code="cs",
                    name="Computer Science",
                    datasource_id=datasource.id,
                ),
                session,
            )
            domain = await self.service._get_domain(
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
        async with self.async_session_factory() as session:
            datasource = await self.datasource_repo.create(
                Datasource(name=DataSource.ARXIV),
                session,
            )

            subject = await self.service._get_subject(
                "cs.AI", datasource.id, DataSource.ARXIV, session
            )
            assert subject is None, "Subject should not be found"

            created_domain = await self.domain_repo.create(
                Domain(
                    code="cs",
                    name="Computer Science",
                    datasource_id=datasource.id,
                ),
                session,
            )
            created_subject = await self.subject_repo.create(
                Subject(
                    code="cs.AI",
                    name="Artificial Intelligence",
                    domain_id=created_domain.id,
                ),
                session,
            )
            subject = await self.service._get_subject(
                "cs.AI", datasource.id, DataSource.ARXIV, session
            )
            assert subject is not None, "Subject should be found"
            assert subject.id == created_subject.id, "Subject ID does not match"
            assert subject.code == created_subject.code, "Subject code does not match"

    async def test_get_or_create_authors(self):
        """Test the list of authors."""
        async with self.async_session_factory() as session:
            datasource = await self.datasource_repo.create(
                Datasource(name=DataSource.ARXIV),
                session,
            )
            paper_authors = ["John Doe", "Jane Doe"]
            authors = await self.service._get_or_create_authors(
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
        async with self.async_session_factory() as session:
            author = await self.author_repo.create(
                Author(name=paper_authors[0]), session
            )
            authors = await self.service._get_or_create_authors(
                paper_authors,
                datasource.id,
                DataSource.ARXIV,
                session,
            )
            assert author == authors[0], "Author does not match"
