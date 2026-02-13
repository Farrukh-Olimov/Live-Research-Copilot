from typing import TYPE_CHECKING

from sqlalchemy import UUID, Boolean, Date, ForeignKey, Integer, Sequence
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel

if TYPE_CHECKING:
    from .datasource import Datasource
    from .paper import Domain


class PaperIngestionState(BaseModel):
    __tablename__ = "paper_ingestion_state"

    id: Mapped[Integer] = mapped_column(
        Integer,
        Sequence("paper_ingestion_state_id_seq"),
        primary_key=True,
        comment="Unique identifier for the paper ingestion state",
    )
    cursor_date: Mapped[Date] = mapped_column(
        Date, nullable=True, comment="Date of the last cursor update"
    )

    datasource_id: Mapped[UUID] = mapped_column(
        ForeignKey("datasources.id"),
        nullable=False,
        index=True,
        comment="ID of the data source (e.g., arXiv, PubMed)",
    )
    datasource: Mapped["Datasource"] = relationship(
        back_populates="paper_ingestion_states",
    )

    domain_id: Mapped[UUID] = mapped_column(
        ForeignKey("domains.id"),
        nullable=False,
        index=True,
        comment="ID of the domain (e.g., Physics)",
    )
    domain: Mapped["Domain"] = relationship(back_populates="paper_ingestion_states")

    is_active: Mapped[Boolean] = mapped_column(Boolean, nullable=False, default=False)
