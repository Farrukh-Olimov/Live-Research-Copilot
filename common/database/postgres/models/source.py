from typing import TYPE_CHECKING, List
from uuid import uuid4

from sqlalchemy import UUID, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel

if TYPE_CHECKING:
    from .paper import Paper


class Source(BaseModel):
    __tablename__ = "sources"
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        default=uuid4,
        nullable=False,
        primary_key=True,
        comment="Unique identifier for the data source (e.g., arXiv, PubMed)",
    )
    name: Mapped[str] = mapped_column(
        String, unique=True, nullable=False, comment="Name of the source"
    )
    papers: Mapped[List["Paper"]] = relationship(
        back_populates="source",
    )
