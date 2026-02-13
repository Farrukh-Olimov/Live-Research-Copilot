from typing import Optional

from sqlalchemy import UUID, select
from sqlalchemy.ext.asyncio import AsyncSession

from common.database.postgres.models import PaperIngestionState

from .base_repository import BaseRepository


class PaperIngestionStateRepository(BaseRepository[PaperIngestionState]):
    def __init__(self):
        """Initializes a PaperIngestionStateRepository object."""
        super().__init__(PaperIngestionState)

    async def get_by_datasource_domain(
        self, domain_id: UUID, datasource_id: UUID, session: AsyncSession
    ) -> Optional[PaperIngestionState]:
        """Get the ingestion state for a specific domain."""
        query = select(PaperIngestionState).where(
            PaperIngestionState.domain_id == domain_id,
            PaperIngestionState.datasource_id == datasource_id,
        )
        rows = await session.execute(query)
        return rows.scalar_one_or_none()
