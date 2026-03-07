from typing import List, Optional

from sqlalchemy import UUID, func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from common.database.postgres.models import Domain, Subject
from common.database.postgres.repositories.base_repository import BaseRepository


class SubjectRepository(BaseRepository[Subject]):
    def __init__(self):
        """Initializes a SubjectRepository object."""
        super().__init__(Subject)

    async def create(self, model: Subject, session: AsyncSession) -> Subject:
        """Creates a model."""
        # TODO: refactor
        smtm = (
            insert(Subject)
            .values(code=model.code, domain_id=model.domain_id, name=model.name)
            .on_conflict_do_nothing(index_elements=["code", "domain_id"])
            .returning(Subject)
        )
        result = await session.execute(smtm)
        row = result.scalar_one_or_none()
        if row is None:
            result = await session.execute(
                select(Subject).where(
                    Subject.domain_id == model.domain_id,
                    Subject.code == model.code,
                )
            )
            row = result.scalar_one()
        return row

    async def get_by_code(self, code: str, session: AsyncSession) -> Optional[Subject]:
        """Returns a subject by code."""
        query = select(Subject).filter_by(code=code)
        rows = await session.execute(query)
        return rows.scalar_one_or_none()

    async def get_by_codes(
        self, codes: List[str], session: AsyncSession
    ) -> List[Subject]:
        """Returns a list of subjects by codes."""
        query = select(Subject).filter(Subject.code.in_(codes))
        rows = await session.execute(query)
        return rows.scalars().all()

    async def get_by_domain_uuid(
        self, domain_uuid: UUID, session: AsyncSession
    ) -> List[Subject]:
        """Returns a list of subjects by domain UUID."""
        query = select(Subject).where(Subject.domain_id == domain_uuid)
        rows = await session.execute(query)
        return rows.scalars().all()

    async def get_subject_domain(self, subject_uuid: UUID, session: AsyncSession):
        """Returns a subject's domain."""
        query = select(Domain).join(Subject.domain).where(Subject.id == subject_uuid)
        rows = await session.execute(query)
        return rows.scalar_one_or_none()

    async def get_by_uuid(self, subject_uuid: UUID, session: AsyncSession):
        """Returns a subject by UUID."""
        query = select(Subject).where(Subject.id == subject_uuid)
        rows = await session.execute(query)
        return rows.scalar_one_or_none()

    async def delete_subject(self, subject: Subject, session: AsyncSession):
        """Deletes a subject."""
        await session.delete(subject)

    async def get_subject_count_by_domain(self, session: AsyncSession):
        """Returns a list of tuples containing the domain name and the subject count.

        Args:
            session (AsyncSession): The database session.

        Returns:
            List[Tuple[str, int]]: A list of tuples (domain name, subject count).
        """
        stmt = (
            select(Domain.name, func.count(Subject.id).label("subject_count"))
            .select_from(Subject)
            .join(Domain, Subject.domain_id == Domain.id)
            .group_by(Domain.name)
        )
        row = await session.execute(stmt)
        return row.all()
