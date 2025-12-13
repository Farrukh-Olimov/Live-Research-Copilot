from typing import ClassVar

from pydantic import BaseModel, Field


class BasePaperSchema(BaseModel):
    source_name: ClassVar[str]


class DomainSchema(BaseModel):
    code: str = Field(description="Domain code")
    name: str = Field(description="Domain name")


class SubjectSchema(BaseModel):
    code: str = Field(description="Subject code")
    name: str = Field(description="Subject name")
    domain: DomainSchema = Field(description="Domain of the subject")
