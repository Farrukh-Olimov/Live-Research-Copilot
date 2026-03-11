from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from common.database.postgres.models import PaperProcessingState

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
