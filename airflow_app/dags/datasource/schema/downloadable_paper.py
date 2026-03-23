from datetime import date
from uuid import UUID
from typing import Optional

from pydantic import BaseModel, Field
from common.storage.s3_location import S3Location


class DownloadablePaper(BaseModel):
    paper_id: UUID = Field(description="Paper id")
    paper_identifier: str = Field(description="Paper identifier")
    datasource_name: str = Field(description="Datasource name")

    location: Optional[S3Location] = Field(
        default=None, description="Location of the downloaded paper"
    )
