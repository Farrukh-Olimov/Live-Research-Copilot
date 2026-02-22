from typing import List, Optional

from sqlalchemy import UUID, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from common.database.postgres.models import PaperIngestionState

from .base_repository import BaseRepository


class PaperIngestionStateRepository(BaseRepository[PaperIngestionState]):
    def __init__(self):
        """Initializes a PaperIngestionStateRepository object."""
        super().__init__(PaperIngestionState)

    async def create(
        self, model: PaperIngestionState, session: AsyncSession
    ) -> PaperIngestionState:
        """Creates a model."""
        try:
            async with session.begin_nested():
                session.add(model)
                await session.flush()
                return model
        except IntegrityError:
            query = select(PaperIngestionState).where(
                PaperIngestionState.datasource_id == model.datasource_id,
                PaperIngestionState.domain_id == model.domain_id,
            )
            result = await session.execute(query)
            return result.scalar_one()

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

    async def get_by_datasource_uuid(
        datasource_uuid: UUID, session: AsyncSession
    ) -> List[PaperIngestionState]:
        """Get the ingestion state for a specific datasource."""
        query = select(PaperIngestionState).where(
            PaperIngestionState.datasource_id == datasource_uuid
        )
        rows = await session.execute(query)
        return rows.scalars().all()

    async def get_active(self, session: AsyncSession) -> List[PaperIngestionState]:
        """Get all active ingestion states."""
        query = select(PaperIngestionState).where(PaperIngestionState.is_active)
        rows = await session.execute(query)
        return rows.scalars().all()
