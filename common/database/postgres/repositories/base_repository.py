from typing import Generic, Type, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeMeta

ModelType = TypeVar("ModelType", bound=DeclarativeMeta)


class BaseRepository(Generic[ModelType]):
    """Base repository with common CRUD operations.

    All specific repositories inherit from this.
    """

    def __init__(self, model: Type[ModelType], session: AsyncSession):
        """Initialize the repository with a model and session.

        Args:
            model: The ORM model class.
            session: The async session to use for database operations.
        """
        self.model = model
        self.session = session
