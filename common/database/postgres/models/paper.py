from datetime import date
from typing import TYPE_CHECKING, List, Optional
from uuid import uuid4

from sqlalchemy import UUID, Date, ForeignKey, Index, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel, TimestampModel
from .relationships import paper_authors

if TYPE_CHECKING:
    from .author import Author
    from .datasource import Datasource
    from .domain import Domain
    from .paper_processing_state import PaperProcessingState
    from .relationships.paper_subject import PaperSubject


class Paper(BaseModel, TimestampModel):
    __tablename__ = "papers"
    __table_args__ = (
        UniqueConstraint(
            "domain_id",
            "datasource_id",
            "paper_identifier",
            name="uq_domain_datasource_paper_identifier",
        ),
        # Hash indexes for UUID FK columns — equality-only lookups, no range queries
        Index("ix_papers_datasource_id", "datasource_id", postgresql_using="hash"),
        Index("ix_papers_domain_id", "domain_id", postgresql_using="hash"),
        Index("ix_papers_main_author_id", "main_author_id", postgresql_using="hash"),
        # B-tree for date — used in range queries (BETWEEN, >, <)
        Index("ix_papers_publish_date", "publish_date"),
        # Composite B-tree — datasource+domain always queried together for ingestion
        Index("ix_papers_datasource_domain", "datasource_id", "domain_id"),
    )
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
        lazy="selectin",
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
        lazy="selectin",
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
        lazy="selectin",
    )

    main_author_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("authors.id"),
        nullable=False,
        comment="ID of the main/primary author of the paper",
    )
    main_author: Mapped["Author"] = relationship(
        foreign_keys=[main_author_id],
        back_populates="primary_papers",
    )

    paper_subjects: Mapped[List["PaperSubject"]] = relationship(
        back_populates="paper",
    )
    processing_state: Mapped[Optional["PaperProcessingState"]] = relationship(
        back_populates="paper",
        uselist=False,
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
        comment="Permanent URL or DOI of the paper",
    )
