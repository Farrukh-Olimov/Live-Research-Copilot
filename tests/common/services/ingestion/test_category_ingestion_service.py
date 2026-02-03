from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from common.database.postgres.models import Datasource
from common.database.postgres.repositories.base_repository import BaseRepository
from common.datasources.schema import SubjectSchema
from common.services.ingestion import CategoryIngestionService


@pytest.mark.asyncio
async def test_category_ingestion_single_subject(
    async_session_factory: async_sessionmaker[AsyncSession],
):
    """Tests that the CategoryIngestionService can ingest a single subject.

    This test ensures that the CategoryIngestionService can ingest a single
    subject into the database. It then asserts that the domain and subject
    are correctly stored in the database.

    Args:
        async_session_factory (async_sessionmaker): The async db session factory.
    """
    datasource_uuid = uuid4()
    datasource = Datasource(id=datasource_uuid, name=datasource_uuid.hex)

    base_repository = BaseRepository(Datasource)
    service = CategoryIngestionService(async_session_factory)

    subject = SubjectSchema(
        code="cs.AI",
        name="Artificial Intelligence",
        domain={
            "code": "cs",
            "name": "Computer Science",
            "datasource_uuid": datasource_uuid,
        },
    )

    await service.ingest_subject(subject)
    async with async_session_factory() as session:
        async with session:
            await base_repository.create(datasource, session)
            domain = await service.domain_repository.get_by_code(
                subject.domain.code, datasource_uuid, session
            )

            assert domain is not None
            assert domain.code == "cs"
            assert domain.name == "Computer Science"

            subject_1 = await service.subject_repository.get_by_code(
                subject.code, session
            )
            await session.commit()

            assert subject_1 is not None
            assert subject_1.code == "cs.AI"
            assert subject_1.name == "Artificial Intelligence"
            assert subject_1.domain_id == domain.id

            await base_repository.delete(datasource, session)
    await service.delete_subject_and_domain(subject)


@pytest.mark.asyncio
async def test_category_ingestion_dubplicate_subject(
    async_session_factory: async_sessionmaker[AsyncSession],
):
    """Tests that the CategoryIngestionService can ingest a duplicate subject.

    This test ensures that the CategoryIngestionService can ingest a duplicate subject
    into the database. It then asserts that the domain and subject are correctly
    stored in the database. It also ensures that the domain and subject are not
    duplicated in the database.

    Args:
        async_session_factory (async_sessionmaker): The async db session factory.
    """
    datasource_uuid = uuid4()
    datasource = Datasource(id=datasource_uuid, name=datasource_uuid.hex)

    base_repository = BaseRepository(Datasource)
    service = CategoryIngestionService(async_session_factory)

    subject = SubjectSchema(
        code="cs.AI",
        name="Artificial Intelligence",
        domain={
            "code": "cs",
            "name": "Computer Science",
            "datasource_uuid": datasource_uuid,
        },
    )

    await service.ingest_subject(subject)
    async with async_session_factory() as session:
        async with session:
            await base_repository.create(datasource, session)
            domain1 = await service.domain_repository.get_by_code(
                subject.domain.code, datasource_uuid, session
            )
            subject1 = await service.subject_repository.get_by_code(
                subject.code, session
            )
            await session.commit()

            await service.ingest_subject(subject)

            domain2 = await service.domain_repository.get_by_code(
                subject.domain.code, datasource_uuid, session
            )
            subject2 = await service.subject_repository.get_by_code(
                subject.code, session
            )
            await session.commit()

            assert domain1 and domain2, "Expected domains to be non empty"
            assert domain1.code == "cs", "Expected domain code to be 'cs'"
            assert (
                domain1.name == "Computer Science"
            ), "Expected domain name to be 'Computer Science'"
            assert domain1.id == domain2.id, "Expected domains to be the same"

            assert subject1 and subject2, "Expected subjects to be non empty"
            assert subject1.code == "cs.AI"
            assert subject1.name == "Artificial Intelligence"
            assert subject1.id == subject2.id, "Expected subjects to be the same"
            assert (
                subject1.domain_id == subject2.domain_id
            ), "Expected domains to be the same"

            await base_repository.delete(datasource, session)
    await service.delete_subject_and_domain(subject)


@pytest.mark.asyncio
async def test_category_ingestion_batch(
    async_session_factory: async_sessionmaker[AsyncSession],
):
    """Tests that the CategoryIngestionService can ingest a batch of subjects.

    Args:
        async_session_factory (async_sessionmaker): The async db session factory.

    Returns:
        None
    """
    datasource_uuid = uuid4()
    datasource = Datasource(id=datasource_uuid, name=datasource_uuid.hex)

    base_repository = BaseRepository(Datasource)
    service = CategoryIngestionService(async_session_factory)

    subject_samples = [
        {"code": "cs.AI", "name": "Artificial Intelligence"},
        {"code": "cs.CS", "name": "Computer Science"},
    ]
    subjects = [
        SubjectSchema(
            domain={
                "code": "cs",
                "name": "Computer Science",
                "datasource_uuid": datasource_uuid,
            },
            **sample,
        )
        for sample in subject_samples
    ]

    await service.ingest_subjects_batch(subjects)

    async with async_session_factory() as session:
        async with session:
            await base_repository.create(datasource, session)
            for i, subject in enumerate(subjects):
                domain = await service.domain_repository.get_by_code(
                    subject.domain.code, datasource_uuid, session
                )
                assert domain is not None
                assert domain.code == "cs"
                assert domain.name == "Computer Science"

                subject_1 = await service.subject_repository.get_by_code(
                    subject.code, session
                )
                assert subject_1 is not None
                assert subject_1.code == subject_samples[i]["code"]
                assert subject_1.name == subject_samples[i]["name"]
                await session.commit()

                await service.delete_subject(subject_1)
            await service.domain_repository.delete_domain(domain, session)
            await base_repository.delete(datasource, session)
            await session.commit()


@pytest.mark.asyncio
async def test_empty_category_ingestion_batch(async_session_factory):
    """Tests that the CategoryIngestionService can ingest an empty list of subjects.

    Args:
        async_session_factory (async_sessionmaker): The async db session factory.

    Returns:
        None
    """
    service = CategoryIngestionService(async_session_factory)

    await service.ingest_subjects_batch([])
