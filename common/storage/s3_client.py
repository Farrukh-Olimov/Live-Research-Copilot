from contextlib import asynccontextmanager
import os
from typing import AsyncGenerator, Optional
from common.storage.storage_configs import S3Bucket, S3PrefixConfig
import aioboto3
from types_aiobotocore_s3 import S3Client
from botocore.exceptions import ClientError
from collections import defaultdict

_s3_session: Optional[aioboto3.Session] = None


def init_s3_session() -> aioboto3.Session:
    """Initializes the S3 client."""
    global _s3_session

    if _s3_session is None:
        _s3_session = aioboto3.Session(
            aws_access_key_id=os.getenv("S3_ACCESS_KEY"),
            aws_secret_access_key=os.getenv("S3_SECRET_ACCESS_KEY"),
        )
    return _s3_session


async def create_s3_bucket(s3_client: S3Client) -> None:
    """Creates an S3 buckets."""
    for bucket_name in S3Bucket:
        try:
            await s3_client.head_bucket(Bucket=bucket_name)
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                await s3_client.create_bucket(Bucket=bucket_name)
            else:
                raise e
        except Exception as e:
            raise e


async def create_s3_lifecycle_rules(s3_client: S3Client) -> None:
    """Creates S3 lifecycle rules."""
    rules_by_bucket = defaultdict(list)
    for s3_location in S3PrefixConfig:
        rules_by_bucket[s3_location.bucket].append(
            {
                "ID": "auto-delete-pdfs",
                "Status": "Enabled",
                "Filter": {"Prefix": s3_location.prefix},
                "Expiration": {"Days": s3_location.expiration_days},
            }
        )
    for bucket, rules in rules_by_bucket.items():
        await s3_client.put_bucket_lifecycle_configuration(
            Bucket=bucket, LifecycleConfiguration={"Rules": rules}
        )


@asynccontextmanager
async def get_s3_client() -> AsyncGenerator[S3Client, None]:
    """Returns the S3 client."""
    global _s3_session
    if _s3_session is None:
        session = init_s3_session()
        async with session.client(
            "s3", endpoint_url=os.getenv("S3_ENDPOINT")
        ) as s3_client:
            await create_s3_bucket(s3_client)
            await create_s3_lifecycle_rules(s3_client)

    async with _s3_session.client(
        "s3", endpoint_url=os.getenv("S3_ENDPOINT")
    ) as s3_client:
        yield s3_client
