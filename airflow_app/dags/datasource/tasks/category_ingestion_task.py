import asyncio
from datetime import datetime, timedelta

from airflow.sdk import task
from httpx import AsyncClient, Limits, Timeout

from common.constants import DataSource
from common.database.postgres.models import Datasource, PaperIngestionState
from common.database.postgres.repositories import DatabaseRepository
from common.database.postgres.session import cleanup, get_session_factory, init_database
from common.datasources.factories import CategoryFetcherFactory
from common.services.ingestion import CategoryIngestionService
from common.utils.logger import LOG_MODULES, LoggerManager

LoggerManager._log_module = LOG_MODULES.AIRFLOW


@task(
    retries=2,
    retry_delay=timedelta(seconds=10),
    retry_exponential_backoff=True,
    max_retry_delay=timedelta(minutes=2),
    sla=timedelta(minutes=5),
    execution_timeout=timedelta(minutes=5),
)
def ingest_categories_task(
    datasource_type: DataSource,
):
    """Run category ingestion for given datasource.

    Args:
        datasource_type (DataSource): The datasource type to ingest.

    Returns:
        None
    """
    logger = LoggerManager.get_logger(__name__)

    async def _run_ingestion(
        datasource_type: DataSource,
    ):
        """Run category ingestion for given datasource.

        Args:
            datasource_type (DataSource): The datasource type to ingest.

        Returns:
            None
        """
        init_database()
        logger.info(
            "Start running category ingestion task.",
            extra={"datasource": datasource_type},
        )

        new_categories = 0

        try:
            db = DatabaseRepository()
            _async_session_factory = get_session_factory()
            async with _async_session_factory() as session:
                async with session.begin():
                    datasource_uuid = await db.datasource.get_uuid_by_name(
                        datasource_type, session
                    )
                    if not datasource_uuid:
                        datasource = Datasource(name=datasource_type)
                        datasource = await db.datasource.create(datasource, session)
                        datasource_uuid = datasource.id
                        logger.debug(
                            "Created datasource",
                            extra={
                                "datasource": datasource_type,
                                "datasource_uuid": datasource_uuid,
                            },
                        )

            async with AsyncClient(
                timeout=Timeout(30), limits=Limits(max_connections=10)
            ) as http_client:
                ingestion_service = CategoryIngestionService(_async_session_factory)
                category_fetcher = CategoryFetcherFactory.get(
                    datasource_type, datasource_uuid, http_client
                )
                async for subject in category_fetcher.fetch_subjects():
                    new_categories += await ingestion_service.ingest_subject(subject)

            logger.info(
                "Category ingestion task completed.",
                extra={"datasource": datasource_type, "new_categories": new_categories},
            )
            # TODO: add metrics

        except Exception as e:
            logger.error(
                "Error running category ingestion task",
                exc_info=e,
                extra={"datasource": datasource_type, "new_categories": new_categories},
            )
            raise e
        finally:
            await cleanup()

    asyncio.run(_run_ingestion(datasource_type))


@task(
    retries=2,
    retry_delay=timedelta(seconds=10),
    retry_exponential_backoff=True,
    max_retry_delay=timedelta(minutes=2),
    sla=timedelta(minutes=5),
    execution_timeout=timedelta(minutes=5),
)
def domain_ingestion_state_task(datasource_type: DataSource):
    """Sets the domain ingestion state for a given datasource.

    Args:
        datasource_type (DataSource): The datasource type to set the ingestion state.

    Returns:
        None
    """
    logger = LoggerManager.get_logger(__name__)

    async def _run_task(datasource_type: DataSource):
        init_database()
        logger.info(
            "Start setting domain ingestion state.",
            extra={"datasource": datasource_type},
        )
        try:
            db = DatabaseRepository()
            _async_session_factory = get_session_factory()
            async with _async_session_factory() as session:
                async with session.begin():
                    datasource_uuid = await db.datasource.get_uuid_by_name(
                        datasource_type, session
                    )
                    if not datasource_uuid:
                        return
                    domains = await db.domain.get_domains_by_datasource_uuid(
                        datasource_uuid, session
                    )
                    for domain in domains:
                        ingestion_state = (
                            await db.paper_ingestion_state.get_by_datasource_domain(
                                domain.id, datasource_uuid, session
                            )
                        )
                        if ingestion_state:
                            continue

                        ingestion_state = PaperIngestionState(
                            datasource_id=datasource_uuid,
                            domain_id=domain.id,
                            cursor_date=datetime(2023, 1, 1),
                            is_active=False,
                        )
                        await db.paper_ingestion_state.create(ingestion_state, session)
        except Exception as e:
            logger.error(
                "Error setting domain ingestion state",
                exc_info=e,
                extra={"datasource": datasource_type},
            )
            raise e
        finally:
            await cleanup()

    asyncio.run(_run_task(datasource_type))
