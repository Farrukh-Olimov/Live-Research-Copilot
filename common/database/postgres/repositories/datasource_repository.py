from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from common.constants.datasource import DataSource
from common.database.postgres.models import Datasource

from .base_repository import BaseRepository


class DatasourceRepository(BaseRepository[Datasource]):
    """Repository for Datasource."""

    def __init__(self):
        """Initializes a DatasourceRepository object.

        Calls the parent's __init__ with Datasource as the model.
        """
        super().__init__(Datasource)

    async def create(self, model: Datasource, session: AsyncSession) -> Datasource:
        """Creates a model."""
        stmt = (
            insert(Datasource)
            .values(name=model.name)
            .on_conflict_do_nothing(index_elements=["name"])
            .returning(Datasource)
        )
        result = await session.execute(stmt)
        row = result.scalar_one_or_none()
        if row is None:
            result = await session.execute(
                select(Datasource).where(Datasource.name == model.name)
            )
            row = result.scalar_one()

        return row

    async def get_uuid_by_name(
        self, datasource_name: DataSource, session: AsyncSession
    ) -> Optional[UUID]:
        """Returns the UUID of the datasource with the given name.

        Args:
            datasource_name: The name of the datasource to find.
            session: The database session.

        Returns:
            UUID: The UUID of the datasource.
        """
        query = select(Datasource.id).where(Datasource.name == datasource_name)
        rows = await session.execute(query)
        return rows.scalar_one_or_none()

    async def get_by_uuid(self, datasource_uuid: UUID, session: AsyncSession):
        """Returns the Datasource with the given UUID.

        Args:
            datasource_uuid: The UUID of the datasource to find.
            session: The database session.

        Returns:
            Datasource: The Datasource with the given UUID, or None if not found.
        """
        query = select(Datasource).where(Datasource.id == datasource_uuid)
        rows = await session.execute(query)
        return rows.scalar_one_or_none()
