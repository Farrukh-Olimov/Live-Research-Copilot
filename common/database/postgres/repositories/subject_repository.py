from typing import List, Optional

from sqlalchemy import UUID, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from common.database.postgres.models import Subject
from common.database.postgres.repositories.base_repository import BaseRepository


class SubjectRepository(BaseRepository[Subject]):
    def __init__(self):
        """Initializes a SubjectRepository object."""
        super().__init__(Subject)

    async def create(self, model: Subject, session: AsyncSession) -> Subject:
        """Creates a model."""
        try:
            async with session.begin_nested():
                session.add(model)
                await session.flush()
                return model
        except IntegrityError:
            query = select(Subject).where(
                Subject.domain_id == model.domain_id,
                Subject.code == model.code,
            )
            result = await session.execute(query)
            return result.scalar_one()

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

    async def get_by_uuid(self, subject_uuid: UUID, session: AsyncSession):
        """Returns a subject by UUID."""
        query = select(Subject).where(Subject.id == subject_uuid)
        rows = await session.execute(query)
        return rows.scalar_one_or_none()

    async def delete_subject(self, subject: Subject, session: AsyncSession):
        """Deletes a subject."""
        await session.delete(subject)
