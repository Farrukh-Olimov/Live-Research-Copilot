from sqlalchemy import UUID, Column, ForeignKey, Table

from ..base import BaseModel

paper_authors = Table(
    "paper_authors",
    BaseModel.metadata,
    Column(
        "author_id",
        UUID(as_uuid=True),
        ForeignKey("authors.id"),
        primary_key=True,
        comment="Reference to Author ID",
    ),
    Column(
        "paper_id",
        UUID(as_uuid=True),
        ForeignKey("papers.id"),
        primary_key=True,
        comment="Reference to Paper ID",
    ),
    comment=(
        "Association table to represent"
        " many-to-many relationship between Papers and Authors"
    ),
)
