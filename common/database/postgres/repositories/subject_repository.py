from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from common.database.postgres.models.subject import Subject
from common.database.postgres.repositories.base_repository import BaseRepository


class SubjectRepository(BaseRepository[Subject]):
    def __init__(self):
        """Initializes a SubjectRepository object."""
        super().__init__(Subject)

    async def get_by_code(self, code: str, session: AsyncSession) -> Subject:
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

    async def delete_subject(self, subject: Subject, session: AsyncSession):
        """Deletes a subject."""
        await session.delete(subject)
