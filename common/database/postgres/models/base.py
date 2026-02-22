from typing import Optional

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column


class BaseModel(DeclarativeBase):
    pass


class TimestampModel:
    @declared_attr
    def created_at(self) -> Mapped[DateTime]:
        """Timestamp of when the object was created."""
        return mapped_column(
            DateTime(timezone=True), nullable=False, server_default=func.now()
        )

    @declared_attr
    def deleted_at(self) -> Mapped[Optional[DateTime]]:
        """Timestamp of when the object was soft-deleted."""
        return mapped_column(DateTime(timezone=True), nullable=True)

    @declared_attr
    def updated_at(self) -> Mapped[DateTime]:
        """Timestamp of when the object was last updated."""
        return mapped_column(
            DateTime(timezone=True), nullable=False, server_default=func.now()
        )
