from typing import List, Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from common.database.postgres.models import Datasource, Paper
from common.database.postgres.models.relationships import PaperSubject, paper_authors

from .base_repository import BaseRepository


class PaperRepository(BaseRepository[Paper]):
    """Paper repository."""

    def __init__(self):
        """Initializes a PaperRepository object.

        Calls the parent's __init__ with Paper as the model.
        """
        super().__init__(Paper)

    async def add_author(
        self, paper_uuid: UUID, author_uuid: UUID, session: AsyncSession
    ):
        """Add an author to a paper."""
        stmt = (
            insert(paper_authors)
            .values(paper_id=paper_uuid, author_id=author_uuid)
            .on_conflict_do_nothing()
        )
        await session.execute(stmt)

    async def create(self, model: Paper, session: AsyncSession) -> Paper:
        """Creates a model."""
        stmt = (
            insert(Paper)
            .values(
                abstract=model.abstract,
                datasource_id=model.datasource_id,
                domain_id=model.domain_id,
                main_author_id=model.main_author_id,
                paper_identifier=model.paper_identifier,
                publish_date=model.publish_date,
                title=model.title,
            )
            .on_conflict_do_nothing(
                index_elements=["domain_id", "datasource_id", "paper_identifier"]
            )
            .returning(Paper)
        )
        result = await session.execute(stmt)
        row = result.scalar_one_or_none()
        if row is None:
            result = await session.execute(
                select(Paper).where(
                    Paper.domain_id == model.domain_id,
                    Paper.datasource_id == model.datasource_id,
                    Paper.paper_identifier == model.paper_identifier,
                )
            )
            row = result.scalar_one()

        return row

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
