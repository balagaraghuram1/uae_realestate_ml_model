"""AWS S3 bucket manager for data and model artifacts."""
import os, logging, hashlib
from typing import Optional, Dict, List
from pathlib import Path

logger = logging.getLogger(__name__)

class S3Manager:
    """Manage files in AWS S3 bucket."""

    def __init__(self, bucket_name: str = None, region: str = "me-south-1"):
        self.bucket_name = bucket_name or os.getenv("S3_BUCKET", "uae-realestate-ml")
        self.region = region
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                import boto3
                self._client = boto3.client("s3", region_name=self.region)
            except ImportError:
                raise RuntimeError("boto3 not installed")
        return self._client

    def upload_file(self, local_path: str, s3_key: str) -> Dict:
        """Upload a file to S3."""
        client = self._get_client()
        file_hash = hashlib.md5(open(local_path, "rb").read()).hexdigest()
        client.upload_file(local_path, self.bucket_name, s3_key)
        logger.info("Uploaded %s to s3://%s/%s", local_path, self.bucket_name, s3_key)
        return {"key": s3_key, "size": os.path.getsize(local_path), "hash": file_hash}

    def download_file(self, s3_key: str, local_path: str) -> str:
        """Download a file from S3."""
        client = self._get_client()
        Path(local_path).parent.mkdir(parents=True, exist_ok=True)
        client.download_file(self.bucket_name, s3_key, local_path)
        logger.info("Downloaded s3://%s/%s to %s", self.bucket_name, s3_key, local_path)
        return local_path

    def list_files(self, prefix: str = "") -> List[Dict]:
        """List files in S3 bucket with prefix."""
        client = self._get_client()
        response = client.list_objects_v2(Bucket=self.bucket_name, Prefix=prefix)
        return [
            {"key": obj["Key"], "size": obj["Size"], "last_modified": str(obj["LastModified"])}
            for obj in response.get("Contents", [])
        ]

    def file_exists(self, s3_key: str) -> bool:
        """Check if a file exists in S3."""
        client = self._get_client()
        try:
            client.head_object(Bucket=self.bucket_name, Key=s3_key)
            return True
        except Exception:
            return False
