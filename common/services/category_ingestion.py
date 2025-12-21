from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from common.database.postgres.models.domain import Domain
from common.database.postgres.models.subject import Subject
from common.database.postgres.repositories import DomainRepository, SubjectRepository
from common.datasources.schema import SubjectSchema


class CategoryIngestionService:
    def __init__(self, session: AsyncSession):
        """Initializes a CategoryIngestionService object.

        Args:
            session (AsyncSession): The SQL Alchemy session to use
                for database operations.

        Returns:
            None
        """
        self.session = session
        self.domain_repository = DomainRepository(session)
        self.subject_repository = SubjectRepository(session)

    async def ingest_subject(self, subject: SubjectSchema):
        """Ingests a subject and its domains into the database.

        Args:
            subject (SubjectSchema): The subject to ingest.

        Returns:
            None
        """
        async with self.session.begin():
            domain = await self.domain_repository.get_by_code(subject.domain.code)

            if not domain:
                domain = Domain(code=subject.domain.code, name=subject.domain.name)
                await self.domain_repository.create(domain=domain)

            existing_subject = await self.subject_repository.get_by_code(subject.code)

            if not existing_subject:
                new_subject = Subject(
                    code=subject.code,
                    name=subject.name,
                    domain_id=domain.id,
                )
                await self.subject_repository.create(subject=new_subject)

    async def ingest_subjects_batch(self, subjects: List[SubjectSchema]):
        """Ingests a batch of subjects and their domains into the database.

        Args:
            subjects (List[SubjectSchema]): A list of subjects to ingest.

        Returns:
            None
        """
        if not subjects:
            return

        async with self.session.begin():
            domain_codes = {subject.domain.code for subject in subjects}
            existing_domains = await self.domain_repository.get_by_codes(domain_codes)
            domain_map = {domain.code: domain for domain in existing_domains}

            new_domains = []
            for subject in subjects:
                domain_code = subject.domain.code
                if domain_code not in domain_map:
                    domain = Domain(
                        code=subject.domain.code,
                        name=subject.domain.name,
                    )
                    new_domains.append(domain)
                    domain_map[domain_code] = domain

            if new_domains:
                await self.domain_repository.create_many(new_domains)

            subject_codes = {subject.code for subject in subjects}
            existing_subjects = await self.subject_repository.get_by_codes(
                subject_codes
            )
            subject_map = {subject.code: subject for subject in existing_subjects}

            new_subjects = []
            for subject in subjects:
                if subject.code not in subject_map:
                    domain = domain_map[subject.domain.code]
                    subject = Subject(
                        code=subject.code,
                        name=subject.name,
                        domain_id=domain.id,
                    )
                    new_subjects.append(subject)
                    subject_map[subject.code] = subject

            if new_subjects:
                await self.subject_repository.create_many(new_subjects)
