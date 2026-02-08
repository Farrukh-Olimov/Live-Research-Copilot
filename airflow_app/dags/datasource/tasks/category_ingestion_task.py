import asyncio

from airflow.sdk import task
from httpx import AsyncClient, Limits, Timeout

from common.constants import DataSource
from common.database.postgres.models import Datasource
from common.database.postgres.repositories import DatasourceRepository
from common.database.postgres.session import (
    cleanup,
    get_session_factory,
    init_database,
)
from common.datasources.factories import CategoryFetcherFactory
from common.services.ingestion import CategoryIngestionService


@task
def ingest_categories_task(
    datasource_type: DataSource,
):
    """Run category ingestion for given datasource.

    Args:
        datasource_type (DataSource): The datasource type to ingest.

    Returns:
        None
    """

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
        datasource_repo = DatasourceRepository()
        _async_session_factory = get_session_factory()
        async with _async_session_factory() as session:
            async with session.begin():
                datasource_uuid = await datasource_repo.get_uuid_by_name(
                    datasource_type, session
                )
                if not datasource_uuid:
                    datasource = Datasource(name=datasource_type)
                    datasource = await datasource_repo.create(datasource, session)
                    datasource_uuid = datasource.id
        async with AsyncClient(
            timeout=Timeout(30), limits=Limits(max_connections=10)
        ) as http_client:
            ingestion_service = CategoryIngestionService(_async_session_factory)
            category_fetcher = CategoryFetcherFactory.create(
                datasource_type, datasource_uuid, http_client
            )
            async for subject in category_fetcher.fetch_subjects():
                await ingestion_service.ingest_subject(subject)

        await cleanup()

    asyncio.run(_run_ingestion(datasource_type))
