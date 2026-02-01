from datetime import datetime

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from common.constants import DataSource
from common.database.postgres.repositories import DomainRepository, SubjectRepository
from common.datasources.factories import PaperMetadataIngestionFactory


class PaperMetadataIngestionService:
    def __init__(
        self,
        factory: PaperMetadataIngestionFactory,
        domain_repository: DomainRepository,
        subject_repository: SubjectRepository,
        http_client: AsyncClient,
        db_session: AsyncSession,
    ):
        # TODO: paper_repository
        """Initializes a PaperMetadataIngestionService object.

        Args:
            factory (PaperMetadataIngestionFactory): The paper metadata ingestion
                factory.
            domain_repository (DomainRepository): The domain repository.
            subject_repository (SubjectRepository): The subject repository.
            http_client (AsyncClient): The http client to use for fetching paper
                metadata.
            db_session (AsyncSession): The database session to use for database
                operations.
        """
        self._factory = factory
        self._domain_repository = domain_repository
        self._subject_repository = subject_repository
        self._http_client = http_client
        self._db_session = db_session

    async def run(
        self,
        datasource_type: DataSource,
        subject: str,
        from_date: datetime,
        until_date: datetime,
    ):
        """Runs the paper metadata ingestion service.

        Args:
            datasource_type (DataSource): The ingestion type to run.
            subject (str): The subject to ingest.
            from_date (datetime): The from date to ingest.
            until_date (datetime): The until date to ingest.

        Yields:
            AsyncIterable[PaperMetadataRecord]: An asynchronous iterable
                of paper metadata records.
        """
        ingestion = self._factory.create(datasource_type, self._http_client)
        domain_code = ingestion._fetcher.get_domain_code(subject)

        async for paper in ingestion.run(subject, from_date, until_date):
            print(domain_code, paper)
            pass
