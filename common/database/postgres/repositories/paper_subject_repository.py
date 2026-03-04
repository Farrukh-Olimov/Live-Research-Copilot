from typing import List

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from common.database.postgres.models import Subject
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

    async def get_paper_count_by_subject(self, session: AsyncSession):
        """Returns a list of tuples containing the subject name and the paper count.

        Args:
            session (AsyncSession): The database session.

        Returns:
            List[Tuple[str, int]]: A list of tuples (subject name, paper count).
        """
        stmt = (
            select(Subject.name, func.count(PaperSubject.paper_id).label("paper_count"))
            .select_from(PaperSubject)
            .join(Subject, PaperSubject.subject_id == Subject.id)
            .group_by(Subject.name)
        )
        row = await session.execute(stmt)
        return row.all()
