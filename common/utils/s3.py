from contextlib import asynccontextmanager
import os
from typing import AsyncGenerator, Optional

import aioboto3
from types_aiobotocore_s3 import S3Client

_s3_session: Optional[aioboto3.Session] = None


def init_s3_session() -> None:
    """Initializes the S3 client."""
    global _s3_session

    if _s3_session is None:
        _s3_session = aioboto3.Session(
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        )


@asynccontextmanager
async def get_s3_client() -> AsyncGenerator[S3Client]:
    """Returns the S3 client."""
    global _s3_session
    if _s3_session is None:
        init_s3_session()

    async with _s3_session.client(
        "s3", endpoint_url=os.getenv("S3_ENDPOINT")
    ) as s3_client:
        yield s3_client


S3Client.put_object()
