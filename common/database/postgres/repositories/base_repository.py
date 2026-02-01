from typing import Generic, Type, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeMeta

ModelType = TypeVar("ModelType", bound=DeclarativeMeta)


class BaseRepository(Generic[ModelType]):
    """Base repository with common CRUD operations.

    All specific repositories inherit from this.
    """

    def __init__(self, model: Type[ModelType]):
        """Initialize the repository with a model and session.

        Args:
            model: The ORM model class.
        """
        self.model = model

    async def create(self, model: ModelType, session: AsyncSession) -> ModelType:
        """Creates a model."""
        session.add(model)
        await session.flush()
        return model

    async def delete(self, model: ModelType, session: AsyncSession):
        """Deletes a model."""
        await session.delete(model)
