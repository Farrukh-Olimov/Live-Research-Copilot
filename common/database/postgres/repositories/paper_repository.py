from typing import List, Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from common.database.postgres.models import Datasource, Paper
from common.database.postgres.models.relationships import PaperSubject

from .base_repository import BaseRepository


class PaperRepository(BaseRepository[Paper]):
    """Paper repository."""

    def __init__(self):
        """Initializes a PaperRepository object.

        Calls the parent's __init__ with Paper as the model.
        """
        super().__init__(Paper)

    async def create(self, model: Paper, session: AsyncSession) -> Paper:
        """Creates a model."""
        # TODO: refactor
        try:
            async with session.begin_nested():
                session.add(model)
                await session.flush()
                return model
        except IntegrityError:
            query = select(Paper).where(
                Paper.domain_id == model.domain_id,
                Paper.datasource_id == model.datasource_id,
                Paper.paper_identifier == model.paper_identifier,
                Paper.title == model.title,
            )
            result = await session.execute(query)
            return result.scalar_one()

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

    async def count_papers(self, datasource_id: UUID, session: AsyncSession) -> int:
        """Counts the number of papers from a given datasource."""
        query = (
            select(func.count())
            .select_from(Paper)
            .where(Paper.datasource_id == datasource_id)
        )
        rows = await session.execute(query)
        return rows.scalar_one()

    async def get_paper_count_by_datasource(self, session: AsyncSession):
        """Counts the number of papers by datasource.

        Args:
            session (AsyncSession): The database session.

        Returns:
            List[Tuple[UUID, int]]: A list of tuples containing the datasource name
                and the paper count.
        """
        stmt = (
            select(Datasource.name, func.count(Paper.id).label("paper_count"))
            .select_from(Paper)
            .join(Datasource, Paper.datasource_id == Datasource.id)
            .group_by(Datasource.name)
        )
        row = await session.execute(stmt)
        return row.all()
