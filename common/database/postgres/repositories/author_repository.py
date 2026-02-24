from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from common.database.postgres.models import Author
from common.utils.logger.logger_config import LoggerManager

from .base_repository import BaseRepository

logger = LoggerManager.get_logger(__name__)


class AuthorRespotitory(BaseRepository[Author]):
    """Repository for Author."""

    def __init__(self):
        """Initializes a AuthorRepository object.

        Calls the parent's __init__ with Author as the model.
        """
        super().__init__(Author)

    async def create(self, model: Author, session: AsyncSession) -> Author:
        """Creates a model."""
        stmt = (
            insert(Author)
            .values(name=model.name)
            .on_conflict_do_nothing(index_elements=["name"])
            .returning(Author)
        )
        result = await session.execute(stmt)
        row = result.scalar_one_or_none()
        if row is None:
            result = await session.execute(
                select(Author).where(Author.name == model.name)
            )
            row = result.scalar_one()

        return row

    async def get_by_name(self, name: str, session: AsyncSession) -> Optional[Author]:
        """Returns the Author with the given name.

        Args:
            name: The name of the author to find.
            session: The database session.

        Returns:
            Optional[Author]: The Author with the given name, or None if not found.
        """
        query = select(Author).where(Author.name == name)
        rows = await session.execute(query)
        return rows.scalar_one_or_none()

    async def get_by_names(
        self, names: List[str], session: AsyncSession
    ) -> List[Author]:
        """Returns the Authors with the given names.

        Args:
            names: The names of the authors to find.
            session: The database session.

        Returns:
            List[Author]: The Authors with the given names.
        """
        query = select(Author).where(Author.name.in_(names))
        rows = await session.execute(query)
        return rows.scalars().all()
