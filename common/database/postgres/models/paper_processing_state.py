from typing import TYPE_CHECKING, Optional
from uuid import uuid4

from sqlalchemy import UUID, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from common.database.postgres.constants import PaperProcessingStatus

from .base import BaseModel, TimestampModel

if TYPE_CHECKING:
    from .paper import Paper


class PaperProcessingState(BaseModel, TimestampModel):
    __tablename__ = "paper_processing_states"
    __table_args__ = (
        # Hash index on UUID FK — equality-only, never range queried
        Index("ix_processing_paper_id", "paper_id", postgresql_using="hash"),
    )
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        default=uuid4,
        nullable=False,
        primary_key=True,
        comment="Unique identifier for the paper processing state",
    )
    paper_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("papers.id"),
        nullable=False,
        unique=True,
        comment="ID of the paper",
    )
    paper: Mapped["Paper"] = relationship(
        back_populates="processing_state",
    )

    status: Mapped[str] = mapped_column(
        String,
        nullable=False,
        default=PaperProcessingStatus.METADATA_INGESTED,
        comment="Status of the paper processing",
    )

    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Populated when status=failed; cleared on successful retry",
    )

    retry_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Number of times this paper has been retried after failure",
    )
