from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from common.database.postgres.constants import PaperProcessingStatus
from common.database.postgres.models import Paper, PaperProcessingState

from .base_repository import BaseRepository


class PaperProcessingStateRepository(BaseRepository[PaperProcessingState]):
    def __init__(self):
        """Initialize a PaperProcessingStateRepository object."""
        super().__init__(PaperProcessingState)

    async def create(self, model: PaperProcessingState, session: AsyncSession):
        """Creates a model."""
        stmt = (
            insert(PaperProcessingState)
            .values(paper_id=model.paper_id)
            .on_conflict_do_nothing(index_elements=["paper_id"])
            .returning(PaperProcessingState)
        )
        result = await session.execute(stmt)
        row = result.scalar_one_or_none()
        if row is None:
            result = await session.execute(
                select(PaperProcessingState).where(
                    PaperProcessingState.paper_id == model.paper_id
                )
            )
            row = result.scalar_one()
        return row

    async def update(
        self, paper_id: UUID, status: PaperProcessingStatus, session: AsyncSession
    ):
        """Updates the status of a paper in the paper processing state table."""
        stmt = (
            update(PaperProcessingState)
            .where(PaperProcessingState.paper_id == paper_id)
            .values(status=status)
            .returning(PaperProcessingState)
        )
        result = await session.execute(stmt)
        row = result.scalar_one()
        return row

    async def claim_papers_by_status(
        self,
        cur_status: PaperProcessingStatus,
        next_status: PaperProcessingStatus,
        batch_size: int,
        session: AsyncSession,
    ):
        """Claims papers by status in the paper processing state table."""
        stmt = (
            select(PaperProcessingState.paper_id)
            .where(PaperProcessingState.status == cur_status)
            .order_by(PaperProcessingState.created_at)
            .limit(batch_size)
            .with_for_update(skip_locked=True)
        )

        row = await session.execute(stmt)

        papers_ids = row.scalars().all()

        if not papers_ids:
            return []

        stmt = (
            update(PaperProcessingState)
            .where(PaperProcessingState.paper_id.in_(papers_ids))
            .values(status=next_status)
        )
        await session.execute(stmt)

        stmt = select(Paper).where(Paper.id.in_(papers_ids))
        row = await session.execute(stmt)
        return row.scalars().all()
