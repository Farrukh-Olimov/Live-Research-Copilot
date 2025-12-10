from typing import TYPE_CHECKING, List
from uuid import uuid4

from sqlalchemy import UUID, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel

if TYPE_CHECKING:
    from .domain import Domain
    from .relationships.paper_subject import PaperSubject


class Subject(BaseModel):
    __tablename__ = "subjects"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        default=uuid4,
        nullable=False,
        primary_key=True,
        comment="Unique identifier for the primary subject",
    )

    code: Mapped[str] = mapped_column(
        String(25),
        nullable=False,
        comment="Code for the primary subject, e.g., CS, Physics",
    )

    domain: Mapped["Domain"] = relationship(back_populates="subjects")

    domain_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("domains.id"),
        nullable=False,
        comment="ID of the high-level academic domain (e.g. Physics)",
    )

    name: Mapped[str] = mapped_column(
        String(25),
        nullable=False,
        comment="Name of the primary subject, e.g., Physics",
    )
    paper_subjects: Mapped[List["PaperSubject"]] = relationship(
        back_populates="subject"
    )
