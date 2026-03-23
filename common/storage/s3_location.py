from pydantic import BaseModel, Field


class S3Location(BaseModel):
    bucket: str = Field(..., env="S3_BUCKET")
    key: str = Field(..., env="S3_KEY")

    @property
    def uri(self) -> str:
        return f"s3://{self.bucket}/{self.key}"
