"""
Context Platform - AWS Helper Utilities
Handles presigned URL generation, cross-account role assumption,
and S3 upload helpers for client data ingestion.

NOTE: Actual AWS calls commented out with stubs for now.
      Uncomment and configure when real credentials are available.
"""

import boto3
import os
from datetime import datetime


# ---------------------------------------------------------------------------
# Config (pulled from env vars — set these in EB environment properties)
# ---------------------------------------------------------------------------
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
CP_S3_BUCKET = os.environ.get("CP_S3_BUCKET", "context-platform-uploads")
CP_ROLE_ARN = os.environ.get("CP_ROLE_ARN", "")  # Your platform's IAM role ARN


# ---------------------------------------------------------------------------
# Generate a pre-signed S3 upload URL for client to use with their own keys
# ---------------------------------------------------------------------------
def generate_presigned_upload_url(client_id: str, filename: str, expiry_seconds: int = 3600) -> dict:
    """
    Generate a pre-signed S3 URL that allows a client to upload
    a file directly to your CP S3 bucket without exposing your AWS keys.

    Workflow:
    1. Your platform generates the URL (using your IAM role)
    2. Client receives the URL
    3. Client uses HTTP PUT directly to S3 (no AWS SDK / keys needed on their end)

    Returns a dict with presigned_url and metadata.
    """
    try:
        s3_client = boto3.client("s3", region_name=AWS_REGION)
        object_key = f"clients/{client_id}/uploads/{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{filename}"

        presigned_url = s3_client.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": CP_S3_BUCKET,
                "Key": object_key,
                "ContentType": "application/octet-stream"
            },
            ExpiresIn=expiry_seconds
        )
        return {
            "success": True,
            "presigned_url": presigned_url,
            "object_key": object_key,
            "bucket": CP_S3_BUCKET,
            "expires_in_seconds": expiry_seconds
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


# ---------------------------------------------------------------------------
# Assume a client's IAM role (cross-account) using their provided role ARN
# ---------------------------------------------------------------------------
def assume_client_role(client_role_arn: str, session_name: str = "CPSession") -> dict:
    """
    Use AWS STS to assume a role in the CLIENT's AWS account.
    Client must first create an IAM role in their account that trusts YOUR account.

    Cross-account trust policy (client creates this in their account):
    {
        "Effect": "Allow",
        "Principal": { "AWS": "arn:aws:iam::YOUR_ACCOUNT_ID:root" },
        "Action": "sts:AssumeRole"
    }
    """
    try:
        sts_client = boto3.client("sts", region_name=AWS_REGION)
        response = sts_client.assume_role(
            RoleArn=client_role_arn,
            RoleSessionName=session_name,
            DurationSeconds=3600
        )
        creds = response["Credentials"]
        return {
            "success": True,
            "access_key_id": creds["AccessKeyId"],
            "secret_access_key": creds["SecretAccessKey"],
            "session_token": creds["SessionToken"],
            "expiration": creds["Expiration"].isoformat()
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


# ---------------------------------------------------------------------------
# List files a client has uploaded to their S3 prefix
# ---------------------------------------------------------------------------
def list_client_uploads(client_id: str) -> dict:
    """List all files a client has uploaded to the CP S3 bucket."""
    try:
        s3_client = boto3.client("s3", region_name=AWS_REGION)
        prefix = f"clients/{client_id}/uploads/"
        response = s3_client.list_objects_v2(
            Bucket=CP_S3_BUCKET,
            Prefix=prefix
        )
        files = []
        for obj in response.get("Contents", []):
            files.append({
                "key": obj["Key"],
                "size_bytes": obj["Size"],
                "last_modified": obj["LastModified"].isoformat()
            })
        return {"success": True, "files": files, "count": len(files)}
    except Exception as e:
        return {"success": False, "error": str(e)}
