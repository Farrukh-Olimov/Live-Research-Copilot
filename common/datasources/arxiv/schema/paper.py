from typing import List, Optional

from pydantic import BaseModel, Field


class ArxivPaper(BaseModel):
    abstract: str = Field(description="Abstract of the paper")
    arxiv_id: str = Field(description="Arxiv ID of the paper")
    authors: List[str] = Field(description="Authors of the paper")
    domain: str = Field(
        description="High-level academic domain (e.g., computer science, physics, math)"
    )
    primary_subject: str = Field(
        description="Primary subject within the domain (e.g., AI, CV, NLP)"
    )
    publish_date: str = Field(description="Date of publication")
    secondary_subject: Optional[str] = Field(
        description="Secondary subject within the domain"
    )
    title: str = Field(description="Title of the paper")
