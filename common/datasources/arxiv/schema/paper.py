from datetime import date
from typing import ClassVar, List, Optional

from pydantic import Field

from common.datasources.arxiv.const import DATASOURCE_NAME
from common.datasources.schema import BasePaperSchema


class ArxivPaperMetadataRecord(BasePaperSchema):
    DATASOURCE_NAME: ClassVar[str] = DATASOURCE_NAME

    abstract: str = Field(description="Abstract of the paper")
    arxiv_id: str = Field(description="Arxiv ID of the paper")
    authors: List[str] = Field(description="Authors of the paper")
    domain: str = Field(
        description="High-level academic domain (e.g., computer science, physics, math)"
    )
    primary_subject: str = Field(
        description="Primary subject within the domain (e.g., AI, CV, NLP)"
    )
    publish_date: date = Field(description="Date of publication")
    secondary_subjects: Optional[List[str]] = Field(
        description="Secondary subject within the domain"
    )
    title: str = Field(description="Title of the paper")
