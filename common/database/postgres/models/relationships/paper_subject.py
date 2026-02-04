from typing import TYPE_CHECKING

from sqlalchemy import UUID, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import BaseModel

if TYPE_CHECKING:
    from ..paper import Paper
    from ..subject import Subject


class PaperSubject(BaseModel):
    __tablename__ = "paper_subjects"

    is_primary: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="Primary subject flag",
    )
    paper: Mapped["Paper"] = relationship(back_populates="paper_subjects")

    paper_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("papers.id"),
        primary_key=True,
        comment="Reference to Paper ID",
    )
    subject_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("subjects.id"),
        primary_key=True,
        comment="Reference to Subject ID",
    )
    subject: Mapped["Subject"] = relationship(
        back_populates="paper_subjects",
        lazy="selectin",
    )
