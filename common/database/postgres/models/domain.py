from typing import TYPE_CHECKING, List
from uuid import uuid4

from sqlalchemy import UUID, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel

if TYPE_CHECKING:
    from .datasource import Datasource
    from .paper import Paper
    from .subject import Subject


class Domain(BaseModel):
    __tablename__ = "domains"
    __table_args__ = (UniqueConstraint("name", "code", name="uq_domain_source_code"),)

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        default=uuid4,
        nullable=False,
        primary_key=True,
        comment="Unique identifier for the academic domain",
    )

    code: Mapped[str] = mapped_column(
        Text, nullable=True, comment="Code for the domain, e.g., CS, Physics"
    )
    datasource_id: Mapped[UUID] = mapped_column(
        ForeignKey("datasources.id"),
        nullable=False,
        index=True,
        comment="ID of the data source (e.g., arXiv, PubMed)",
    )
    datasource: Mapped["Datasource"] = relationship(
        back_populates="domains",
    )

    name: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Name of the domain, e.g., Computer Science, Physics",
    )

    papers: Mapped[List["Paper"]] = relationship(
        back_populates="domain",
    )

    subjects: Mapped[List["Subject"]] = relationship(
        back_populates="domain",
    )
