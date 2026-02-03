from typing import List

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from common.database.postgres.models import Domain, Subject
from common.database.postgres.repositories import DomainRepository, SubjectRepository
from common.datasources.schema import SubjectSchema
from common.utils.logger.logger_config import LoggerManager

logger = LoggerManager.get_logger(__name__)


class CategoryIngestionService:
    def __init__(self, db_session_factory: async_sessionmaker[AsyncSession]):
        """Initializes a CategoryIngestionService object.

        Args:
            db_session_factory (async_sessionmaker): The async session factory.

        Returns:
            None
        """
        self.db_session_factory = db_session_factory
        self.domain_repository = DomainRepository()
        self.subject_repository = SubjectRepository()

    async def ingest_subject(self, subject: SubjectSchema):
        """Ingests a subject and its domains into the database.

        Args:
            subject (SubjectSchema): The subject to ingest.

        Returns:
            None
        """
        async with self.db_session_factory() as session:
            async with session.begin():
                domain = await self.domain_repository.get_by_code(
                    subject.domain.code, subject.domain.datasource_uuid, session
                )

                if not domain:
                    try:
                        domain = Domain(
                            code=subject.domain.code,
                            name=subject.domain.name,
                            datasource_id=subject.domain.datasource_uuid,
                        )
                        await self.domain_repository.create(domain, session)
                    except IntegrityError:
                        logger.warning(
                            "Domain code already exists",
                            extra={"domain": subject.domain},
                        )
                        domain = await self.domain_repository.get_by_code(
                            subject.domain.code, subject.domain.datasource_uuid, session
                        )

                existing_subject = await self.subject_repository.get_by_code(
                    subject.code, session
                )

                if not existing_subject:
                    try:
                        new_subject = Subject(
                            code=subject.code,
                            name=subject.name,
                            domain_id=domain.id,
                        )
                        await self.subject_repository.create(new_subject, session)
                    except IntegrityError:
                        logger.warning(
                            "Subject already exists", extra={"subject": subject}
                        )

    async def ingest_subjects_batch(self, subjects: List[SubjectSchema]):
        """Ingests a batch of subjects and their domains into the database.

        Args:
            subjects (List[SubjectSchema]): A list of subjects to ingest.

        Returns:
            None
        """
        if not subjects:
            logger.info("No subjects to ingest")
            return
        async with self.db_session_factory() as session:
            async with session.begin():
                domain_codes = {subject.domain.code for subject in subjects}
                datasource_uuids = {
                    subject.domain.datasource_uuid for subject in subjects
                }

                existing_domains = await self.domain_repository.get_by_codes(
                    domain_codes, datasource_uuids, session
                )
                domain_map = {
                    (domain.code, domain.datasource_id): domain
                    for domain in existing_domains
                }

                new_domains = []
                for subject in subjects:
                    domain_code = subject.domain.code
                    datasource_uuid = subject.domain.datasource_uuid
                    if (domain_code, datasource_uuid) not in domain_map:
                        domain = Domain(
                            code=domain_code,
                            name=subject.domain.name,
                            datasource_id=datasource_uuid,
                        )
                        new_domains.append(domain)
                        domain_map[(domain_code, datasource_uuid)] = domain

                if new_domains:
                    await self.domain_repository.create_many(new_domains, session)

                subject_codes = {subject.code for subject in subjects}
                existing_subjects = await self.subject_repository.get_by_codes(
                    subject_codes, session
                )
                subject_map = {subject.code: subject for subject in existing_subjects}

                new_subjects = []
                for subject in subjects:
                    if subject.code not in subject_map:
                        domain_code = subject.domain.code
                        datasource_uuid = subject.domain.datasource_uuid
                        domain = domain_map[(domain_code, datasource_uuid)]
                        subject = Subject(
                            code=subject.code,
                            name=subject.name,
                            domain_id=domain.id,
                        )
                        new_subjects.append(subject)
                        subject_map[subject.code] = subject

                if new_subjects:
                    await self.subject_repository.create_many(new_subjects, session)

    async def delete_subject(self, subject: SubjectSchema):
        """Removes only a subject from the database.

        Args:
            subject (SubjectSchema): The subject to remove.

        Returns:
            None
        """
        async with self.db_session_factory() as session:
            async with session.begin():
                subject = await self.subject_repository.get_by_code(
                    subject.code, session
                )
                logger.info("Deleting subject", extra={"subject": subject})
                await self.subject_repository.delete_subject(subject, session)

    async def delete_subject_and_domain(self, subject: SubjectSchema):
        """Removes a subject and its domain from the database.

        Args:
            subject (SubjectSchema): The subject to remove.

        Returns:
            None
        """
        async with self.db_session_factory() as session:
            async with session.begin():
                subject_1 = await self.subject_repository.get_by_code(
                    subject.code, session
                )
                domain_1 = await self.domain_repository.get_by_code(
                    subject.domain.code, subject.domain.datasource_uuid, session
                )
                logger.info(
                    "Deleting subject and domain",
                    extra={"subject": subject},
                )
                await self.subject_repository.delete_subject(subject_1, session)
                await self.domain_repository.delete_domain(domain_1, session)
