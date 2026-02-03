import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from common.services.ingestion import PaperMetadataIngestionService
from common.database.postgres.models import Datasource
from common.database.postgres.repositories import (
    AuthorRespotitory,
    DatasourceRepository,
    DomainRepository,
    PaperRepository,
    SubjectRepository,
)
from common.datasources.factories import PaperMetadataIngestionFactory
from common.constants import DataSource


@pytest.mark.asyncio
async def test_datasource_uuid(async_session_factory: async_sessionmaker[AsyncSession]):
    datasource_repo = DatasourceRepository()
    paper_ingestion_service = PaperMetadataIngestionService(
        PaperMetadataIngestionFactory(),
        AuthorRespotitory(),
        datasource_repo,
        DomainRepository(),
        PaperRepository(),
        SubjectRepository(),
        async_session_factory,
        None,  # httpx client is not needed
    )
    async with async_session_factory() as session:
        with pytest.raises(ValueError):
            await paper_ingestion_service._get_datasource_uuid(
                DataSource.ARXIV, session
            )
        new_datasource = Datasource(name=DataSource.ARXIV)
        datasource_1 = await datasource_repo.create(new_datasource, session)

        assert datasource_1 is not None, "Datasource should be created."

        datasource_uuid = await datasource_repo.get_uuid_by_name(
            datasource_name=DataSource.ARXIV, session=session
        )
        assert datasource_uuid is not None, "Datasource should be found."
        assert datasource_1.id == datasource_uuid, "Datasource should be the same."
