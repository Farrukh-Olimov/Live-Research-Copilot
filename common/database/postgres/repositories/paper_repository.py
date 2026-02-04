from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from common.database.postgres.models import Paper
from common.database.postgres.models.relationships import PaperSubject

from .base_repository import BaseRepository


class PaperRepository(BaseRepository[Paper]):
    """Paper repository."""

    def __init__(self):
        """Initializes a PaperRepository object.

        Calls the parent's __init__ with Paper as the model.
        """
        super().__init__(Paper)

    async def get_by_title(self, title: str, session: AsyncSession) -> Optional[Paper]:
        """Get a paper by title."""
        query = select(Paper).where(Paper.title == title)
        rows = await session.execute(query)
        return rows.scalar_one_or_none()

    async def get_by_paper_id(
        self, paper_id: str, session: AsyncSession
    ) -> Optional[Paper]:
        """Get a paper by source ID (URL)."""
        query = select(Paper).where(Paper.paper_identifier == paper_id)
        rows = await session.execute(query)
        return rows.scalar_one_or_none()

    async def add_subjects(self, subjects: List[PaperSubject], session: AsyncSession):
        """Add subjects to a paper."""
        session.add_all(subjects)
        await session.flush()
