from common.datasources.factories import PaperMetadataIngestionFactory
from common.constants import DataSource
from datetime import datetime
from httpx import AsyncClient
from common.database.postgres.repositories import DomainRepository, SubjectRepository
from sqlalchemy.ext.asyncio import AsyncSession


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
        ingestion = self._factory.create(datasource_type, self._http_client)
        domain_code = ingestion._fetcher.get_domain_code(subject)
        

        async for paper in ingestion.run(subject, from_date, until_date):
            pass    
