from datetime import date
from typing import TYPE_CHECKING, List
from uuid import uuid4

from sqlalchemy import UUID, Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel, TimestampModel
from .relationships import paper_authors

if TYPE_CHECKING:
    from .author import Author
    from .domain import Domain
    from .relationships.paper_subject import PaperSubject
    from .datasource import Datasource


class Paper(BaseModel, TimestampModel):
    __tablename__ = "papers"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        default=uuid4,
        nullable=False,
        primary_key=True,
        comment="Unique identifier for the paper",
    )
    authors: Mapped[List["Author"]] = relationship(
        secondary=paper_authors,
        back_populates="publications",
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

    paper_subjects: Mapped[List["PaperSubject"]] = relationship(
        back_populates="paper",
    )
    publish_date: Mapped[date] = mapped_column(
        Date, nullable=False, comment="Date of publication"
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
    title: Mapped[str] = mapped_column(
        String, nullable=False, comment="Title of the paper"
    )
    url: Mapped[str] = mapped_column(
        String,
        nullable=False,
        unique=True,
        comment="Permanent URL or DOI of the paper",
    )
