from typing import List, Optional

from sqlalchemy import UUID, func, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from common.database.postgres.models import Paper, PaperIngestionState

from .base_repository import BaseRepository


class PaperIngestionStateRepository(BaseRepository[PaperIngestionState]):
    def __init__(self):
        """Initializes a PaperIngestionStateRepository object."""
        super().__init__(PaperIngestionState)

    async def create(
        self, model: PaperIngestionState, session: AsyncSession
    ) -> PaperIngestionState:
        """Creates a model."""
        stmt = (
            insert(PaperIngestionState)
            .values(
                domain_id=model.domain_id,
                datasource_id=model.datasource_id,
                cursor_date=model.cursor_date,
                is_active=model.is_active,
            )
            .on_conflict_do_nothing(index_elements=["datasource_id", "domain_id"])
            .returning(PaperIngestionState)
        )
        result = await session.execute(stmt)
        row = result.scalar_one_or_none()
        if row is None:
            result = await session.execute(
                select(PaperIngestionState).where(
                    PaperIngestionState.domain_id == model.domain_id,
                    PaperIngestionState.datasource_id == model.datasource_id,
                )
            )
            row = result.scalar_one()
        return row

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

    async def update_cursor_date_from_papers(
        self,
        session: AsyncSession,
    ):
        """Update the cursor date for a specific domain."""
        sub_query = (
            select(
                Paper.domain_id,
                Paper.datasource_id,
                func.max(Paper.publish_date).label("cursor_date"),
            )
            .group_by(Paper.domain_id, Paper.datasource_id)
            .subquery()
        )

        query = (
            update(PaperIngestionState)
            .values(cursor_date=sub_query.c.cursor_date)
            .where(
                PaperIngestionState.domain_id == sub_query.c.domain_id,
                PaperIngestionState.datasource_id == sub_query.c.datasource_id,
                PaperIngestionState.cursor_date < sub_query.c.cursor_date,
            )
        )

        await session.execute(query)
