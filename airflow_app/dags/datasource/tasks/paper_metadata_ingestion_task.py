import asyncio
from datetime import timedelta
from typing import List
from uuid import UUID

from airflow.sdk import task
from dags.datasource.schema import PaperIngestionStateRecord, SubjectIngestionRecord
from httpx import AsyncClient, Limits, Timeout

from common.database.postgres.repositories import DatabaseRepository
from common.database.postgres.session import cleanup, get_session_factory, init_database
from common.datasources.factories import PaperMetadataIngestionFactory
from common.services.ingestion import PaperMetadataIngestionService
from common.utils.logger.logger_config import LOG_MODULES, LoggerManager

LoggerManager._log_module = LOG_MODULES.AIRFLOW


@task(
    retries=2,
    retry_delay=timedelta(seconds=5),
    retry_exponential_backoff=True,
    max_retry_delay=timedelta(minutes=2),
    sla=timedelta(minutes=5),
    execution_timeout=timedelta(minutes=5),
)
def load_domain_ingestion_states() -> List[PaperIngestionStateRecord]:
    """Loads domain ingestion states for a all datasources.

    Args:
        datasource_type (DataSource): The datasource type to load ingestion states for.

    Returns:
        List[PaperIngestionStateRecord]: A list of domain ingestion states for the
            given datasource type.
    """
    logger = LoggerManager.get_logger(__name__)
    logger.info("Loading domain ingestion states")

    async def _run_ingestion():
        init_database()
        _async_session_factory = get_session_factory()
        _db = DatabaseRepository()
        domain_state_records = []
        try:
            async with _async_session_factory() as session:
                domain_states = await _db.paper_ingestion_state.get_active(session)

                for domain_state in domain_states:
                    domain_state_records.append(
                        PaperIngestionStateRecord(
                            datasource_uuid=UUID(str(domain_state.datasource_id)),
                            domain_uuid=UUID(str(domain_state.domain_id)),
                            cursor_date=domain_state.cursor_date,
                            is_active=bool(domain_state.is_active),
                        ).model_dump(mode="json")
                    )
        except Exception as e:
            logger.error(
                "Error running domain ingestion task",
                exc_info=e,
            )
            raise e
        finally:
            logger.info(
                "Domain ingestion states loaded",
                extra={"count": len(domain_state_records)},
            )
            await cleanup()
        return domain_state_records

    return asyncio.run(_run_ingestion())


@task(
    retries=2,
    retry_delay=timedelta(seconds=5),
    retry_exponential_backoff=True,
    max_retry_delay=timedelta(minutes=2),
    sla=timedelta(minutes=5),
    execution_timeout=timedelta(minutes=5),
)
def load_subject_to_ingest(
    ingestion_state: PaperIngestionStateRecord,
) -> List[SubjectIngestionRecord]:
    """Loads the subject to ingest given the ingestion state.

    Args:
        ingestion_state (PaperIngestionStateRecord): The ingestion state to
            load the subject for.

    Returns:
        List[SubjectIngestionRecord]: A list of subjects to ingest for the
            given ingestion state.
    """
    logger = LoggerManager.get_logger(__name__)
    logger.info("Loading subject to ingest", extra={"ingestion_state": ingestion_state})

    async def _run_ingestion(ingestion_state: PaperIngestionStateRecord):

        init_database()
        _async_session_factory = get_session_factory()
        _db = DatabaseRepository()
        subject_records: List[SubjectIngestionRecord] = []
        try:
            async with _async_session_factory() as session:
                subjects = await _db.subject.get_by_domain_uuid(
                    ingestion_state.domain_uuid, session
                )
                for subject in subjects:
                    subject_records.append(
                        SubjectIngestionRecord(
                            datasource_uuid=UUID(str(ingestion_state.datasource_uuid)),
                            domain_uuid=UUID(str(ingestion_state.domain_uuid)),
                            subject_uuid=UUID(str(subject.id)),
                            from_date=ingestion_state.cursor_date,
                            until_date=ingestion_state.cursor_date + timedelta(days=10),
                        ).model_dump(mode="json")
                    )
        except Exception:
            logger.error(
                "Error running subject ingestion task",
                exc_info=True,
                extra={"ingestion_state": ingestion_state},
            )
        finally:
            logger.info(
                "Subject to ingest loaded",
                extra={"count": len(subject_records)},
            )
            await cleanup()
        return subject_records

    if ingestion_state is None:
        return None
    ingestion_state = PaperIngestionStateRecord.model_validate(ingestion_state)
    return asyncio.run(_run_ingestion(ingestion_state))


@task(
    retries=2,
    retry_delay=timedelta(seconds=5),
    retry_exponential_backoff=True,
    max_retry_delay=timedelta(minutes=2),
    sla=timedelta(minutes=5),
    execution_timeout=timedelta(minutes=5),
)
def flatten(records) -> List:
    """Flatten a list of records."""
    logger = LoggerManager.get_logger(__name__)

    new_records = []
    queue = []
    for record in records:
        queue.append(record)

    while queue:
        record = queue.pop()
        if isinstance(record, list):
            queue.extend(record)
        elif record is not None:
            new_records.append(record)
    logger.info("Flattened records", extra={"count": len(new_records)})
    return new_records


@task(
    retries=5,
    retry_delay=timedelta(minutes=5),
    retry_exponential_backoff=True,
    max_retry_delay=timedelta(minutes=10),
    sla=timedelta(hours=2),
    execution_timeout=timedelta(hours=4),
)
def ingest_papers_task(subject_record: SubjectIngestionRecord):
    """Runs the paper metadata ingestion task for the given datasource type.

    Args:
        subject_record (SubjectIngestionRecord): The subject record to run the
             ingestion task for.

    Returns:
        None
    """
    logger = LoggerManager.get_logger(__name__)
    logger.info("Running paper ingestion task")

    async def _run_ingestion(subject_record: SubjectIngestionRecord):
        init_database()
        _async_session_factory = get_session_factory()
        _factory = PaperMetadataIngestionFactory()
        _db = DatabaseRepository()

        ingested_papers_count = 0
        try:
            async with AsyncClient(
                timeout=Timeout(30), limits=Limits(max_connections=10)
            ) as http_client:
                metadata_ingestion_service = PaperMetadataIngestionService(
                    _factory, _db, _async_session_factory, http_client
                )

                ingested_papers_count: int = await metadata_ingestion_service.run(
                    datasource_uuid=subject_record.datasource_uuid,
                    subject_uuid=subject_record.subject_uuid,
                    from_date=subject_record.from_date,
                    until_date=subject_record.until_date,
                )

        except Exception as e:
            logger.error(
                "Error running paper ingestion task",
                exc_info=e,
                extra={"subject_record": subject_record},
            )
            raise e
        finally:
            await cleanup()

        logger.info(
            "Paper ingestion task completed",
            extra={
                "subject_record": subject_record,
                "num_papers_ingested": ingested_papers_count,
            },
        )

    if subject_record is None:
        return None
    subject_record = SubjectIngestionRecord.model_validate(subject_record)
    return asyncio.run(_run_ingestion(subject_record))


@task(
    retries=2,
    retry_delay=timedelta(seconds=10),
    retry_exponential_backoff=True,
    max_retry_delay=timedelta(minutes=2),
    sla=timedelta(minutes=5),
    execution_timeout=timedelta(minutes=5),
)
def update_domain_ingestion_states():
    """Updates the domain ingestion states with the latest cursor dates.

    Returns:
        None
    """
    logger = LoggerManager.get_logger(__name__)
    logger.info("Updating domain ingestion states")

    async def _run_ingestions():
        init_database()
        _async_session_factory = get_session_factory()
        _db = DatabaseRepository()

        try:
            async with _async_session_factory() as session:
                async with session.begin():
                    await _db.paper_ingestion_state.update_cursor_date_from_papers(
                        session
                    )

        except Exception as e:
            logger.error(
                "Error running domain ingestion task",
                exc_info=e,
            )
        finally:
            await cleanup()

    return asyncio.run(_run_ingestions())
