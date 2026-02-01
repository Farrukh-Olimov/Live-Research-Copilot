from datetime import date
from typing import ClassVar, List
from uuid import UUID

from pydantic import BaseModel, Field


class BasePaperSchema(BaseModel):
    DATASOURCE_NAME: ClassVar[str]


class DomainSchema(BaseModel):
    code: str = Field(description="Domain code")
    name: str = Field(description="Domain name")
    datasource_uuid: UUID = Field(description="UUID of the datasource")


class SubjectSchema(BaseModel):
    code: str = Field(description="Subject code")
    name: str = Field(description="Subject name")
    domain: DomainSchema = Field(description="Domain of the subject")


class PaperMetadataRecord(BaseModel):
    abstract: str = Field(description="Abstract of the paper")
    authors: List[str] = Field(description="Authors of the paper")
    domain_code: str = Field(description="High-level academic domain")
    paper_id: str = Field(description="Paper ID")
    primary_subject_code: str = Field(description="Primary subject within the domain")
    publish_date: date = Field(description="Date of publication")
    secondary_subject_codes: List[str] = Field(
        description=" Secondary subjects within the domains"
    )
    source: str = Field(description="Source of the paper")
    title: str = Field(description="Title of the paper")
