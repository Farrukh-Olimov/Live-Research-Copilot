from datetime import datetime

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from common.constants import DataSource
from common.database.postgres.repositories import (
    DatasourceRepository,
    DomainRepository,
    SubjectRepository,
)
from common.datasources.factories import PaperMetadataIngestionFactory
from common.database.postgres.models.domain import Domain
from common.utils.logger.logger_config import LoggerManager

logger = LoggerManager.get_logger(__name__)


class PaperMetadataIngestionService:
    def __init__(
        self,
        factory: PaperMetadataIngestionFactory,
        datasource_repository: DatasourceRepository,
        domain_repository: DomainRepository,
        subject_repository: SubjectRepository,
        db_session_factory: async_sessionmaker[AsyncSession],
        http_client: AsyncClient,
    ):
        # TODO: paper_repository
        """Initializes a PaperMetadataIngestionService object.

        Args:
            factory (PaperMetadataIngestionFactory): The paper metadata ingestion
                factory.
            datasource_repository (DatasourceRepository): The datasource repository.
            domain_repository (DomainRepository): The domain repository.
            subject_repository (SubjectRepository): The subject repository.
            db_session_factory (async_sessionmaker): The async session factory.
            http_client (AsyncClient): The httpx client to use for fetching paper
                metadata.

        """
        self._factory = factory
        self._datasource_repository = datasource_repository
        self._domain_repository = domain_repository
        self._subject_repository = subject_repository
        self._http_client = http_client
        self._db_session_factory = db_session_factory

    async def run(
        self,
        datasource_type: DataSource,
        subject: str,
        from_date: datetime,
        until_date: datetime,
    ):

        ingestion = self._factory.create(datasource_type, self._http_client)
        domain_code = ingestion._fetcher.get_domain_code(subject)
        datasource_uuid = None

        async with self._db_session_factory() as session:
            async with session:
                datasource_uuid = await self._datasource_repository.get_uuid_by_name(
                    datasource_type, session
                )

        if datasource_uuid is None:
            raise ValueError(f"Datasource {datasource_type} not found")

        async for paper in ingestion.run(subject, from_date, until_date):
            async with self._db_session_factory() as session:
                async with session.begin():

                    domain = await self._domain_repository.get_by_code(
                        paper.domain_code, datasource_uuid, session
                    )

                    if not domain:
                        logger.error(
                            "Domain not found",
                            extra={
                                "domain_code": paper.domain_code,
                                "datasource": datasource_type,
                                "datasource_uuid": datasource_uuid,
                            },
                        )
                        continue

                    subject = await self._subject_repository.get_by_code(
                        paper.primary_subject_code, session
                    )

                    if not subject:
                        logger.error(
                            "Subject not found",
                            extra={
                                "subject_code": paper.primary_subject_code,
                                "datasource": datasource_type,
                                "datasource_uuid": datasource_uuid,
                            },
                        )
                        continue
                    secondary_subjects = self._subject_repository.get_by_codes(
                        paper.secondary_subject_codes, session
                    )

                    