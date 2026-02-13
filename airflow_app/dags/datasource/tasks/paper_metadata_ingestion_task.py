import asyncio
from datetime import datetime

from airflow.sdk import task
from httpx import AsyncClient, Limits, Timeout

from common.database.postgres.models import Datasource
from common.database.postgres.repositories import DatabaseRepository
from common.database.postgres.session import cleanup, get_session_factory, init_database
from common.datasources.factories import PaperMetadataIngestionFactory
from common.services.ingestion import PaperMetadataIngestionService
from common.utils.logger.logger_config import LoggerManager

logger = LoggerManager.get_logger(__name__)


@task
def ingest_papers_task(datasource_type: Datasource, from_data: datetime):
    """Runs the paper metadata ingestion task for the given datasource type.

    Args:
        datasource_type (DataSource): The datasource type to ingest.
        from_data (datetime): The from date to ingest.

    Returns:
        None
    """

    async def _run_ingestion(
        datasource_type: Datasource,
        from_data: datetime,
    ):
        init_database()
        _async_session_factory = get_session_factory()
        _factory = PaperMetadataIngestionFactory()
        _database_repo = DatabaseRepository()
        try:
            async with AsyncClient(
                timeout=Timeout(30), limits=Limits(max_connections=10)
            ) as http_client:
                metadata_ingestion_service = PaperMetadataIngestionService(
                    _factory, _database_repo, _async_session_factory, http_client
                )

                await metadata_ingestion_service.run(
                    datasource_type, subject=None, from_date=from_data, until_date=None
                )
        except Exception as e:
            logger.error(
                "Error running paper ingestion task",
                exc_info=e,
                extra={"datasource": datasource_type},
            )
            raise e
        finally:
            await cleanup()

    asyncio.run(_run_ingestion(datasource_type, from_data))
