import pytest

from common.datasources.schema import SubjectSchema
from common.services.category_ingestion import CategoryIngestionService


@pytest.mark.asyncio
async def test_category_ingestion_single_subject(session):
    """Tests that the CategoryIngestionService can ingest a single subject.

    This test ensures that the CategoryIngestionService can ingest a single
    subject into the database. It then asserts that the domain and subject
    are correctly stored in the database.

    Args:
        session (AsyncSession): The SQL Alchemy session to use
            for database operations.
    """
    service = CategoryIngestionService(session)

    subject = SubjectSchema(
        code="cs.AI",
        name="Artificial Intelligence",
        domain={
            "code": "cs",
            "name": "Computer Science",
        },
    )

    await service.ingest_subject(subject)

    domain = await service.domain_repository.get_by_code(subject.domain.code)

    assert domain is not None
    assert domain.code == "cs"
    assert domain.name == "Computer Science"

    subject = await service.subject_repository.get_by_code(subject.code)
    await session.commit()

    assert subject is not None
    assert subject.code == "cs.AI"
    assert subject.name == "Artificial Intelligence"
    assert subject.domain_id == domain.id

    await service.delete_subject_and_domain(subject)


@pytest.mark.asyncio
async def test_category_ingestion_dubplicate_subject(session):
    """Tests that the CategoryIngestionService can ingest a duplicate subject.

    This test ensures that the CategoryIngestionService can ingest a duplicate subject
    into the database. It then asserts that the domain and subject are correctly
    stored in the database. It also ensures that the domain and subject are not
    duplicated in the database.

    Args:
        session (AsyncSession): The SQL Alchemy session to use
            for database operations.
    """
    service = CategoryIngestionService(session)

    subject = SubjectSchema(
        code="cs.AI",
        name="Artificial Intelligence",
        domain={
            "code": "cs",
            "name": "Computer Science",
        },
    )

    await service.ingest_subject(subject)
    domain1 = await service.domain_repository.get_by_code(subject.domain.code)
    subject1 = await service.subject_repository.get_by_code(subject.code)
    await session.commit()
    await service.ingest_subject(subject)
    domain2 = await service.domain_repository.get_by_code(subject.domain.code)
    subject2 = await service.subject_repository.get_by_code(subject.code)
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
    assert subject1.domain_id == subject2.domain_id, "Expected domains to be the same"

    await service.delete_subject_and_domain(subject)


@pytest.mark.asyncio
async def test_category_ingestion_batch(session):
    """Tests that the CategoryIngestionService can ingest a batch of subjects.

    Args:
        session (AsyncSession): The SQL Alchemy session.

    Returns:
        None
    """
    service = CategoryIngestionService(session)

    subject_samples = [
        {"code": "cs.AI", "name": "Artificial Intelligence"},
        {"code": "cs.CS", "name": "Computer Science"},
    ]
    subjects = [
        SubjectSchema(
            domain={
                "code": "cs",
                "name": "Computer Science",
            },
            **sample,
        )
        for sample in subject_samples
    ]

    await service.ingest_subjects_batch(subjects)

    for i, subject in enumerate(subjects):
        domain = await service.domain_repository.get_by_code(subject.domain.code)
        assert domain is not None
        assert domain.code == "cs"
        assert domain.name == "Computer Science"

        subject = await service.subject_repository.get_by_code(subject.code)
        assert subject is not None
        assert subject.code == subject_samples[i]["code"]
        assert subject.name == subject_samples[i]["name"]
        await session.commit()

        await service.delete_subject(subject)
    await service.domain_repository.delete_domain(domain)

    await session.commit()


@pytest.mark.asyncio
async def test_empty_category_ingestion_batch(session):
    """Tests that the CategoryIngestionService can ingest an empty list of subjects.

    Args:
        session (AsyncSession): The SQL Alchemy session.

    Returns:
        None
    """
    service = CategoryIngestionService(session)

    await service.ingest_subjects_batch([])
