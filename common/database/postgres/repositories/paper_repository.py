from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from common.constants.datasource import DataSource
from common.database.postgres.models import Paper
from typing import Optional
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
