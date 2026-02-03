from datetime import datetime
from typing import List, Optional
from uuid import UUID

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from common.constants import DataSource
from common.database.postgres.models import Author, Domain, Paper, Subject
from common.database.postgres.models.relationships import PaperSubject
from common.database.postgres.repositories import (
    AuthorRespotitory,
    DatasourceRepository,
    DomainRepository,
    PaperRepository,
    SubjectRepository,
)
from common.datasources.factories import PaperMetadataIngestionFactory
from common.datasources.schema import PaperMetadataRecord
from common.utils.logger.logger_config import LoggerManager

logger = LoggerManager.get_logger(__name__)


class PaperMetadataIngestionService:
    def __init__(
        self,
        factory: PaperMetadataIngestionFactory,
        author_repository: AuthorRespotitory,
        datasource_repository: DatasourceRepository,
        domain_repository: DomainRepository,
        paper_repository: PaperRepository,
        subject_repository: SubjectRepository,
        db_session_factory: async_sessionmaker[AsyncSession],
        http_client: AsyncClient,
    ):
        # TODO: paper_repository
        """Initializes a PaperMetadataIngestionService object.

        Args:
            factory (PaperMetadataIngestionFactory): The paper metadata ingestion
                factory.
            author_repository (AuthorRespotitory): The author repository.
            datasource_repository (DatasourceRepository): The datasource repository.
            domain_repository (DomainRepository): The domain repository.
            paper_repository (PaperRepository): The paper repository.
            subject_repository (SubjectRepository): The subject repository.
            db_session_factory (async_sessionmaker): The async session factory.
            http_client (AsyncClient): The httpx client to use for fetching paper
                metadata.

        """
        self._factory = factory
        self._author_repository = author_repository
        self._datasource_repository = datasource_repository
        self._domain_repository = domain_repository
        self._paper_repository = paper_repository
        self._subject_repository = subject_repository
        self._http_client = http_client
        self._db_session_factory = db_session_factory

    async def _get_or_create_paper(
        self,
        paper_metadata: PaperMetadataRecord,
        authors: List[Author],
        domain: Domain,
        primary_subject: Subject,
        secondary_subjects: List[Subject],
        datasource_uuid: UUID,
        session: AsyncSession,
    ):
        """Gets or creates a paper from the database.

        Args:
            paper_metadata (PaperMetadataRecord): The paper metadata to create.
            authors (List[Author]): The authors of the paper.
            domain (Domain): The domain of the paper.
            primary_subject (Subject): The primary subject of the paper.
            secondary_subjects (List[Subject]): The secondary subjects of the paper.
            datasource_uuid (UUID): The UUID of the datasource.
            session (AsyncSession): The database session.

        Returns:
            Paper: The paper found or created, or None.
        """
        paper = await self._paper_repository.get_by_title(paper_metadata.title, session)
        if paper:
            logger.info(
                "Paper already exists",
                extra={"paper": paper.title, "paper_id": paper.id},
            )
            return None

        paper = Paper(
            abstract=paper_metadata.abstract,
            datasource_id=datasource_uuid,
            domain_id=domain.id,
            main_author_id=authors[0].id,
            publish_date=paper_metadata.publish_date,
            title=paper_metadata.title,
            url=paper_metadata.source,
        )

        paper = await self._paper_repository.create(paper, session)
        if paper is None:
            logger.error(
                "Failed to create paper",
                extra={
                    "paper": paper_metadata.title,
                },
            )
            return None

        paper.paper_subjects.append(
            PaperSubject(
                is_primary=True,
                subject_id=primary_subject.id,
            )
        )
        paper.paper_subjects.extend(
            [
                PaperSubject(
                    is_primary=False,
                    subject_id=subject.id,
                )
                for subject in secondary_subjects
            ]
        )

    async def _paper_orchestrator(
        self,
        paper: PaperMetadataRecord,
        datasource_uuid: UUID,
        datasource_type: DataSource,
        session: AsyncSession,
    ) -> Optional[Paper]:
        """Orchestrates the ingestion of a paper.

        Args:
            paper (PaperMetadataRecord): The paper to ingest.
            datasource_uuid (UUID): The UUID of the datasource.
            datasource_type (DataSource): The type of the datasource.
            session (AsyncSession): The database session.

        Returns:
            Optional[Paper]: The ingested paper, or None if the ingestion failed.
        """
        domain = await self._get_domain(
            paper.domain_code, datasource_uuid, datasource_type, session
        )
        if domain is None:
            return None

        # Get subjects
        subject = await self._get_subject(
            paper.primary_subject_code,
            datasource_uuid,
            datasource_type,
            session,
        )
        if subject is None:
            return None

        secondary_subjects = self._subject_repository.get_by_codes(
            paper.secondary_subject_codes, session
        )

        authors = await self._get_or_create_authors(
            paper.authors, datasource_uuid, datasource_type, session
        )
        if not authors:
            return None

        paper = await self._get_or_create_paper(
            paper,
            authors,
            domain,
            subject,
            secondary_subjects,
            datasource_uuid,
            datasource_type,
            session,
        )
        return paper

    async def run(
        self,
        datasource_type: DataSource,
        subject: str,
        from_date: datetime,
        until_date: datetime,
    ):
        """Runs the paper metadata ingestion given subject and date range.

        Args:
            datasource_type (DataSource): The datasource type to ingest.
            subject (str): The subject to ingest.
            from_date (datetime): The from date to ingest.
            until_date (datetime): The until date to ingest.

        Yields:
            AsyncIterator[PaperMetadataRecord]: An asynchronous iterator
                of paper metadata records.
        """
        ingestion = self._factory.create(datasource_type, self._http_client)
        datasource_uuid = None

        async with self._db_session_factory() as session:
            async with session:
                datasource_uuid = await self._get_datasource_uuid(
                    datasource_type, session
                )

            async for paper in ingestion.run(subject, from_date, until_date):
                async with session.begin():
                    await self._paper_orchestrator(
                        paper, datasource_uuid, datasource_type, session
                    )

    async def _get_datasource_uuid(
        self, datasource_type: DataSource, session: AsyncSession
    ):
        """Returns the UUID of the datasource with the given type.

        Args:
            datasource_type (DataSource): The type of the datasource to find.
            session (AsyncSession): The database session.

        Returns:
            UUID: The UUID of the datasource.

        Raises:
            ValueError: If the datasource is not found.
        """
        datasource_uuid = await self._datasource_repository.get_uuid_by_name(
            datasource_type, session
        )
        if datasource_uuid is None:
            raise ValueError(
                "Datasource  not found", extra={"datasource": datasource_type}
            )
        return datasource_uuid

    async def _get_domain(
        self,
        domain_code: str,
        datasource_uuid: UUID,
        datasource_type: DataSource,
        session: AsyncSession,
    ) -> Optional[Domain]:
        """Returns a domain by code and datasource UUID.

        Args:
            domain_code (str): The code of the domain to find.
            datasource_uuid (UUID): The UUID of the datasource.
            datasource_type (DataSource): The type of the datasource.
            session (AsyncSession): The database session.

        Returns:
            Optional[Domain]: The domain found, or None if the domain is not found.
        """
        domain = await self._domain_repository.get_by_code(
            domain_code, datasource_uuid, session
        )
        if domain is None:
            logger.error(
                "Domain not found",
                extra={
                    "domain_code": domain_code,
                    "datasource": datasource_type,
                    "datasource_uuid": datasource_uuid,
                },
            )
        return domain

    async def _get_subject(
        self,
        subject_code: str,
        datasource_uuid: UUID,
        datasource_type: DataSource,
        session: AsyncSession,
    ) -> Optional[Subject]:
        """Returns a subject by code and datasource UUID.

        Args:
            subject_code (str): The code of the subject to find.
            datasource_uuid (UUID): The UUID of the datasource.
            datasource_type (DataSource): The type of the datasource.
            session (AsyncSession): The database session.

        Returns:
            Optional[Subject]: The subject found, or None if the subject is not found.
        """
        subject = await self._subject_repository.get_by_code(subject_code, session)
        if subject is None:
            logger.error(
                "Subject not found",
                extra={
                    "subject_code": subject_code,
                    "datasource": datasource_type,
                    "datasource_uuid": datasource_uuid,
                },
            )
        return subject

    async def _get_or_create_authors(
        self,
        paper_authors: List[str],
        datasource_uuid: UUID,
        datasource_type: DataSource,
        session: AsyncSession,
    ) -> List[Author]:
        """Gets or creates authors in the database.

        Args:
            paper_authors (List[str]): The authors of the paper.
            datasource_uuid (UUID): The UUID of the datasource.
            datasource_type (DataSource): The type of the datasource.
            session (AsyncSession): The database session.

        Returns:
            List[Author]: The authors found or created.
        """
        # Get Authors
        database_authors = await self._author_repository.get_by_names(
            paper_authors, session
        )
        authors = []
        if len(database_authors) != len(paper_authors):
            author_names = [author.name for author in database_authors]
            for paper_author in paper_authors:
                if paper_author not in author_names:
                    logger.info("Creating author", extra={"author": paper_author})
                    author = Author(name=paper_author)
                    authors.append(
                        await self._author_repository.create(author, session)
                    )
                else:
                    index = author_names.index(paper_author)
                    authors.append(database_authors[index])
        else:
            authors = database_authors

        if not authors:
            logger.error(
                "No authors found",
                extra={
                    "authors": paper_authors,
                    "datasource": datasource_type,
                    "datasource_uuid": datasource_uuid,
                },
            )
        return authors
