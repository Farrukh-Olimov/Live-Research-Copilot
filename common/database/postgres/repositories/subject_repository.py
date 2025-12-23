from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from common.database.postgres.models.subject import Subject
from common.database.postgres.repositories.base_repository import BaseRepository


class SubjectRepository(BaseRepository[Subject]):
    def __init__(self, session: AsyncSession):
        """Initializes a SubjectRepository object.

        Args:
            session (AsyncSession): The async session to use for database operations.
        """
        super().__init__(Subject, session)

    async def create(self, subject: Subject) -> Subject:
        """Creates a subject."""
        self.session.add(subject)
        await self.session.flush()
        return subject

    async def create_many(self, subjects: List[Subject]) -> List[Subject]:
        """Creates batch of subjects."""
        self.session.add_all(subjects)
        await self.session.flush()
        return subjects

    async def get_by_code(self, code: str) -> Subject:
        """Returns a subject by code."""
        query = select(Subject).filter_by(code=code)
        rows = await self.session.execute(query)
        return rows.scalar_one_or_none()

    async def get_by_codes(self, codes: List[str]) -> List[Subject]:
        """Returns a list of subjects by codes."""
        query = select(Subject).filter(Subject.code.in_(codes))
        rows = await self.session.execute(query)
        return rows.scalars().all()

    async def delete_subject(self, subject: Subject):
        """Deletes a subject."""
        await self.session.delete(subject)
