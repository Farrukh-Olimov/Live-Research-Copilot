from datetime import date
from uuid import UUID

from pydantic import BaseModel, Field


class PaperIngestionStateRecord(BaseModel):
    cursor_date: date = Field(description="Date of the last cursor update")
    datasource_uuid: UUID = Field(description="UUID of the datasource")
    domain_uuid: UUID = Field(description="UUID of the domain")
    is_active: bool = Field(description="Whether the ingestion state is active")
    is_updated: bool = Field(
        default=False, description="Whether the ingestion state is updated"
    )
