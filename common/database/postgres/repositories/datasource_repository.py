from uuid import UUID

from sqlalchemy import select
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

    async def get_uuid_by_name(
        self, datasource_name: DataSource, session: AsyncSession
    ) -> UUID:
        """Returns the UUID of the datasource with the given name.

        Args:
            datasource_name: The name of the datasource to find.
            session: The database session.

        Returns:
            UUID: The UUID of the datasource.
        """
        query = select(Datasource.id).where(DataSource.name == datasource_name)
        rows = await session.execute(query)
        return rows.scalar_one_or_none()
