from datetime import date
from typing import TYPE_CHECKING, List
from uuid import uuid4

from sqlalchemy import UUID, Date, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel, TimestampModel
from .relationships import paper_authors

if TYPE_CHECKING:
    from .author import Author
    from .datasource import Datasource
    from .domain import Domain
    from .relationships.paper_subject import PaperSubject


class Paper(BaseModel, TimestampModel):
    __tablename__ = "papers"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        default=uuid4,
        nullable=False,
        primary_key=True,
        comment="Unique identifier for the paper",
    )
    abstract: Mapped[str] = mapped_column(
        Text, nullable=False, comment="Abstract of the paper"
    )

    authors: Mapped[List["Author"]] = relationship(
        secondary=paper_authors,
        back_populates="publications",
    )

    datasource_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("datasources.id"),
        comment=(
            "ID of the source from which this paper"
            " was ingested (e.g., arXiv, PubMed)"
        ),
    )
    datasource: Mapped["Datasource"] = relationship(
        foreign_keys=[datasource_id],
        back_populates="papers",
    )

    domain_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("domains.id"),
        comment=(
            "ID of the high-level academic domain (e.g., Computer Science, Physics)"
        ),
    )
    domain: Mapped["Domain"] = relationship(
        foreign_keys=[domain_id],
        back_populates="papers",
    )

    main_author_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("authors.id"),
        comment="ID of the main/primary author of the paper",
    )
    main_author: Mapped["Author"] = relationship(
        foreign_keys=[main_author_id],
        back_populates="primary_papers",
    )

    paper_subjects: Mapped[List["PaperSubject"]] = relationship(
        back_populates="paper",
        lazy="selectin",
    )
    publish_date: Mapped[date] = mapped_column(
        Date, nullable=False, comment="Date of publication"
    )

    title: Mapped[str] = mapped_column(
        Text, nullable=False, comment="Title of the paper"
    )

    paper_identifier: Mapped[str] = mapped_column(
        String,
        nullable=False,
        unique=True,
        comment="Permanent URL or DOI of the paper",
    )
