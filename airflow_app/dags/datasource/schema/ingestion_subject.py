from datetime import date
from uuid import UUID

from pydantic import BaseModel, Field


class SubjectIngestionRecord(BaseModel):
    datasource_uuid: UUID = Field(description="Datasource type uuid")
    domain_uuid: UUID = Field(description="Domain uuid")
    subject_uuid: UUID = Field(description="Subject uuid")
    from_date: date = Field(description="From date")
    until_date: date = Field(description="Until date")
