import asyncio
from datetime import datetime

from airflow.sdk import task

from common.constants import DataSource
from common.database.postgres.models import PaperIngestionState
from common.database.postgres.repositories import DatabaseRepository
from common.database.postgres.session import (
    cleanup,
    get_session_factory,
    init_database,
)
from common.utils.logger.logger_config import LoggerManager

logger = LoggerManager.get_logger(__name__)


@task
def domain_ingestion_state_task(datasource_type: DataSource):
    """Sets the domain ingestion state for a given datasource.

    Args:
        datasource_type (DataSource): The datasource type to set the ingestion state.

    Returns:
        None
    """

    async def _run_task(datasource_type: DataSource):
        logger.info(f"Setting domain ingestion state for {datasource_type}")
        init_database()
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
                                datasource_uuid, domain.id, session
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
