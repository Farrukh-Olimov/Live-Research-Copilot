import asyncio
from datetime import timedelta
from typing import List
from uuid import UUID

from dags.datasource.schema import PaperIngestionStateRecord, SubjectIngestionRecord
from httpx import AsyncClient, Limits, Timeout

from common.database.postgres.repositories import DatabaseRepository
from common.database.postgres.session import cleanup, get_session_factory, init_database
from common.datasources.factories import PaperMetadataIngestionFactory
from common.services.ingestion import PaperMetadataIngestionService
from common.utils.logger.logger_config import LoggerManager

logger = LoggerManager.get_logger(__name__)


# @task
def load_domain_ingestion_states() -> List[PaperIngestionStateRecord]:
    """Loads domain ingestion states for a all datasources.

    Args:
        datasource_type (DataSource): The datasource type to load ingestion states for.

    Returns:
        List[PaperIngestionStateRecord]: A list of domain ingestion states for the
            given datasource type.
    """
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
                        )
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


# @task
def load_subject_to_ingest(ingestion_state: PaperIngestionStateRecord):
    """Loads the subject to ingest given the ingestion state.

    Args:
        ingestion_state (PaperIngestionStateRecord): The ingestion state to
            load the subject for.

    Returns:
        List[SubjectIngestionRecord]: A list of subjects to ingest for the
            given ingestion state.
    """

    async def _run_ingestion(ingestion_state: PaperIngestionStateRecord):
        logger.info(
            "Loading subject to ingest", extra={"ingestion_state": ingestion_state}
        )
        init_database()
        _async_session_factory = get_session_factory()
        _db = DatabaseRepository()
        subject_records = []
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
                        )
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

    return asyncio.run(_run_ingestion(ingestion_state))


# @task
def ingest_papers_task(subject_record: SubjectIngestionRecord):
    """Runs the paper metadata ingestion task for the given datasource type.

    Args:
        subject_record (SubjectIngestionRecord): The subject record to run the
             ingestion task for.

    Returns:
        None
    """

    async def _run_ingestion(subject_record: SubjectIngestionRecord):
        init_database()
        _async_session_factory = get_session_factory()
        _factory = PaperMetadataIngestionFactory()
        _db = DatabaseRepository()

        is_inserted = False
        try:
            async with AsyncClient(
                timeout=Timeout(30), limits=Limits(max_connections=10)
            ) as http_client:
                metadata_ingestion_service = PaperMetadataIngestionService(
                    _factory, _db, _async_session_factory, http_client
                )

                is_inserted = await metadata_ingestion_service.run(
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

        ingestion_state = None
        if is_inserted:
            logger.info(
                "Paper ingestion task completed",
                extra={"subject_record": subject_record},
            )
            ingestion_state = PaperIngestionStateRecord(
                datasource_uuid=subject_record.datasource_uuid,
                domain_uuid=subject_record.domain_uuid,
                cursor_date=subject_record.until_date,
                is_active=True,
            )
        return ingestion_state

    asyncio.run(_run_ingestion(subject_record))
