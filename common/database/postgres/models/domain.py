from typing import TYPE_CHECKING, List, Optional
from uuid import uuid4

from sqlalchemy import UUID, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel

if TYPE_CHECKING:
    from .paper import Paper


class Domain(BaseModel):
    __tablename__ = "domains"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        default=uuid4,
        nullable=False,
        primary_key=True,
        comment="Unique identifier for the academic domain",
    )
    description: Mapped[Optional[str]] = mapped_column(
        String, nullable=True, comment="Description of the domain"
    )
    name: Mapped[str] = mapped_column(
        String,
        unique=True,
        nullable=False,
        comment="Name of the domain, e.g., Computer Science, Physics",
    )

    papers: Mapped[List["Paper"]] = relationship(
        back_populates="domain",
    )
