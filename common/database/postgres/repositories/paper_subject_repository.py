from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from common.database.postgres.models.relationships import PaperSubject

from .base_repository import BaseRepository


class PaperSubjectRepository(BaseRepository[PaperSubject]):
    """PaperSubject repository."""

    def __init__(self):
        """Initializes a PaperSubjectRepository object."""
        super().__init__(PaperSubject)

    async def add_subject_to_paper(
        self, paper_subject: PaperSubject, session: AsyncSession
    ):
        """Add a subject to a paper."""
        session.add(paper_subject)
        await session.flush()

    async def add_subjects_to_paper(
        self, paper_subjects: List[PaperSubject], session: AsyncSession
    ):
        """Add subjects to a paper."""
        session.add_all(paper_subjects)
        await session.flush()
