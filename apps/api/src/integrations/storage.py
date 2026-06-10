"""S3-compatible storage service (MinIO local / AWS S3 production)."""

import boto3
import structlog
from botocore.config import Config
from botocore.exceptions import ClientError

from src.core.config import settings

logger = structlog.get_logger()

_s3_client = None


def _get_s3_client():
    """Get or create a cached S3 client.

    Uses the endpoint URL, access key, and secret key from settings.
    """
    global _s3_client
    if _s3_client is not None:
        return _s3_client

    _s3_client = boto3.client(
        "s3",
        endpoint_url=settings.S3_ENDPOINT,
        aws_access_key_id=settings.S3_ACCESS_KEY,
        aws_secret_access_key=settings.S3_SECRET_KEY,
        config=Config(signature_version="s3v4"),
        region_name="us-east-1",
    )
    return _s3_client


def ensure_bucket(bucket: str | None = None) -> bool:
    """Ensure the S3 bucket exists, creating it if necessary.

    Returns True if the bucket is ready, False on failure.
    """
    bucket = bucket or settings.S3_BUCKET
    s3 = _get_s3_client()
    try:
        s3.head_bucket(Bucket=bucket)
    except ClientError as e:
        if e.response["Error"]["Code"] == "404":
            try:
                s3.create_bucket(Bucket=bucket)
                logger.info("s3_bucket_created", bucket=bucket)
            except ClientError as create_err:
                logger.error("s3_bucket_create_failed", bucket=bucket, error=str(create_err))
                return False
        else:
            logger.error("s3_bucket_check_failed", bucket=bucket, error=str(e))
            return False
    return True


def upload_fileobj(fileobj, key: str, content_type: str, bucket: str | None = None) -> str | None:
    """Upload a file-like object to S3.

    Args:
        fileobj: A binary file-like object (e.g. from FastAPI UploadFile).
        key: The object key / path in the bucket.
        content_type: MIME type (e.g. "image/jpeg").
        bucket: S3 bucket name. Defaults to settings.S3_BUCKET.

    Returns:
        The public URL of the uploaded object, or None on failure.
    """
    bucket = bucket or settings.S3_BUCKET
    s3 = _get_s3_client()

    if not ensure_bucket(bucket):
        return None

    try:
        s3.upload_fileobj(
            fileobj,
            bucket,
            key,
            ExtraArgs={
                "ContentType": content_type,
                "CacheControl": "public, max-age=31536000, immutable",
            },
        )
        url = f"{settings.S3_ENDPOINT}/{bucket}/{key}"
        logger.info("s3_upload_success", bucket=bucket, key=key, url=url)
        return url
    except ClientError as e:
        logger.error("s3_upload_failed", bucket=bucket, key=key, error=str(e))
        return None


def delete_object(key: str, bucket: str | None = None) -> bool:
    """Delete an object from S3.

    Args:
        key: The object key / path in the bucket.
        bucket: S3 bucket name. Defaults to settings.S3_BUCKET.

    Returns:
        True if deleted or not found, False on failure.
    """
    bucket = bucket or settings.S3_BUCKET
    s3 = _get_s3_client()

    try:
        s3.delete_object(Bucket=bucket, Key=key)
        logger.info("s3_delete_success", bucket=bucket, key=key)
        return True
    except ClientError as e:
        logger.error("s3_delete_failed", bucket=bucket, key=key, error=str(e))
        return False
