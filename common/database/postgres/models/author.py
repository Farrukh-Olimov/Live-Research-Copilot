from typing import TYPE_CHECKING, List
from uuid import uuid4

from sqlalchemy import UUID, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel
from .relationships import paper_authors

if TYPE_CHECKING:
    from .paper import Paper


class Author(BaseModel):
    __tablename__ = "authors"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        default=uuid4,
        nullable=False,
        primary_key=True,
        comment="Unique identifier for the author",
    )
    name: Mapped[str] = mapped_column(
        String, unique=True, comment="Full name of the author"
    )
    primary_papers: Mapped[List["Paper"]] = relationship(
        back_populates="main_author",
        foreign_keys="Paper.main_author_id",
    )
    publications: Mapped[List["Paper"]] = relationship(
        secondary=paper_authors,
        back_populates="authors",
    )
