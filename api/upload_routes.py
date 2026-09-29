"""
Context Platform - Client Data Upload API Route
Exposes endpoints for clients to get presigned URLs, upload files directly,
or pull data using client AWS credentials/roles.
"""

import json
import boto3
import botocore
import os
from datetime import datetime
from flask import Blueprint, request, jsonify
from api.context_routes import _context_store

uploads_bp = Blueprint("uploads", __name__, url_prefix="/api/v1/uploads")

CP_S3_BUCKET = os.environ.get("CP_S3_BUCKET", "context-platform-uploads")
AWS_REGION   = os.environ.get("AWS_REGION", "us-east-1")


# ---------------------------------------------------------------------------
# POST /api/v1/uploads/direct
# Direct File Upload Endpoint (Drag & Drop from web UI / API)
# ---------------------------------------------------------------------------
@uploads_bp.route("/direct", methods=["POST"])
def direct_upload():
    """
    Accepts direct file upload (multipart/form-data or binary) from the UI.
    Stores the raw file in S3/Context Store and creates an associated context entry.
    """
    client_id = request.form.get("client_id") or request.args.get("client_id")
    if not client_id and request.is_json:
        body = request.get_json(silent=True) or {}
        client_id = body.get("client_id")

    if not client_id:
        return jsonify({"success": False, "error": "client_id is required"}), 400

    if "file" not in request.files:
        return jsonify({"success": False, "error": "No file included in upload request"}), 400

    uploaded_file = request.files["file"]
    filename = uploaded_file.filename or "uploaded_data.file"
    file_bytes = uploaded_file.read()

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    object_key = f"clients/{client_id}/uploads/{timestamp}_{filename}"

    # Try storing to S3 if configured
    s3_uploaded = False
    try:
        s3 = boto3.client("s3", region_name=AWS_REGION)
        s3.put_object(
            Bucket=CP_S3_BUCKET,
            Key=object_key,
            Body=file_bytes,
            ContentType=uploaded_file.content_type or "application/octet-stream"
        )
        s3_uploaded = True
    except Exception:
        # Fallback to local context store registration if AWS S3 credentials are mock/offline
        pass

    # Automatically construct a Context Entry so AI agents can query it immediately
    context_type = "file_ingestion"
    parsed_content = None

    if filename.endswith(".json"):
        try:
            parsed_content = json.loads(file_bytes.decode("utf-8"))
            context_type = "json_dataset"
        except Exception:
            parsed_content = {"raw_text": file_bytes.decode("utf-8", errors="ignore")}
    elif filename.endswith(".csv") or filename.endswith(".txt"):
        try:
            text_str = file_bytes.decode("utf-8", errors="ignore")
            lines = [l.strip() for l in text_str.splitlines() if l.strip()]
            parsed_content = {
                "filename": filename,
                "row_count": len(lines),
                "preview": lines[:10],
                "raw_text": text_str[:5000]
            }
            context_type = "csv_dataset" if filename.endswith(".csv") else "document"
        except Exception:
            parsed_content = {"filename": filename, "file_size_bytes": len(file_bytes)}
    else:
        parsed_content = {
            "filename": filename,
            "content_type": uploaded_file.content_type,
            "size_bytes": len(file_bytes)
        }

    context_id = f"ctx_{timestamp}_{os.urandom(4).hex()}"
    entry = {
        "context_id": context_id,
        "client_id": client_id,
        "context_type": context_type,
        "data": parsed_content,
        "tags": ["direct_upload", filename.split(".")[-1]],
        "aws_region": AWS_REGION,
        "s3_path": f"s3://{CP_S3_BUCKET}/{object_key}" if s3_uploaded else "local_store",
        "created_at": datetime.utcnow().isoformat()
    }
    _context_store[context_id] = entry

    return jsonify({
        "success": True,
        "message": "File uploaded and registered as Context Entry successfully!",
        "context_id": context_id,
        "filename": filename,
        "bytes_received": len(file_bytes),
        "s3_key": object_key if s3_uploaded else None,
        "context_entry": entry
    }), 200


# ---------------------------------------------------------------------------
# POST /api/v1/uploads/presigned-url
# Client requests a presigned upload URL — NO AWS keys needed on their end
# ---------------------------------------------------------------------------
@uploads_bp.route("/presigned-url", methods=["POST"])
def get_presigned_url():
    body = request.get_json(silent=True) or {}
    client_id = body.get("client_id")
    filename  = body.get("filename", "upload.csv")

    if not client_id:
        return jsonify({"success": False, "error": "client_id is required"}), 400

    expiry = int(body.get("expiry_seconds", 3600))
    content_type = body.get("content_type", "application/octet-stream")

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    object_key = f"clients/{client_id}/uploads/{timestamp}_{filename}"

    try:
        s3 = boto3.client("s3", region_name=AWS_REGION)
        url = s3.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": CP_S3_BUCKET,
                "Key": object_key,
                "ContentType": content_type
            },
            ExpiresIn=expiry
        )
        return jsonify({
            "success": True,
            "presigned_url": url,
            "object_key": object_key,
            "bucket": CP_S3_BUCKET,
            "method": "PUT",
            "expires_in_seconds": expiry,
            "instructions": (
                f"HTTP PUT your file body to the presigned_url with "
                f"Content-Type: {content_type}"
            )
        }), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ---------------------------------------------------------------------------
# POST /api/v1/uploads/via-client-keys
# Client provides their own AWS temp creds to push data
# ---------------------------------------------------------------------------
@uploads_bp.route("/via-client-keys", methods=["POST"])
def upload_via_client_keys():
    body = request.get_json(silent=True) or {}

    required = ["client_id", "aws_access_key_id", "aws_secret_access_key",
                "source_bucket", "source_key"]
    missing = [f for f in required if not body.get(f)]
    if missing:
        return jsonify({"success": False, "error": f"Missing fields: {missing}"}), 400

    client_id = body["client_id"]

    try:
        session = boto3.Session(
            aws_access_key_id=body["aws_access_key_id"],
            aws_secret_access_key=body["aws_secret_access_key"],
            aws_session_token=body.get("aws_session_token"),
            region_name=body.get("aws_region", AWS_REGION)
        )
        client_s3 = session.client("s3")

        obj = client_s3.get_object(
            Bucket=body["source_bucket"],
            Key=body["source_key"]
        )
        data_bytes = obj["Body"].read()

        dest_key = (
            f"clients/{client_id}/uploads/"
            f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_"
            f"{body['source_key'].split('/')[-1]}"
        )
        cp_s3 = boto3.client("s3", region_name=AWS_REGION)
        cp_s3.put_object(
            Bucket=CP_S3_BUCKET,
            Key=dest_key,
            Body=data_bytes
        )

        return jsonify({
            "success": True,
            "message": "Data pulled from client bucket and ingested into CP",
            "dest_key": dest_key,
            "dest_bucket": CP_S3_BUCKET,
            "bytes_ingested": len(data_bytes)
        }), 200

    except botocore.exceptions.ClientError as e:
        code = e.response["Error"]["Code"]
        return jsonify({
            "success": False,
            "error": f"AWS error [{code}]: {str(e)}"
        }), 403
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ---------------------------------------------------------------------------
# POST /api/v1/uploads/assume-role
# Platform assumes client's cross-account IAM role to pull their data
# ---------------------------------------------------------------------------
@uploads_bp.route("/assume-role", methods=["POST"])
def upload_via_assumed_role():
    body = request.get_json(silent=True) or {}

    required = ["client_id", "client_role_arn", "source_bucket", "source_key"]
    missing = [f for f in required if not body.get(f)]
    if missing:
        return jsonify({"success": False, "error": f"Missing fields: {missing}"}), 400

    client_id = body["client_id"]

    try:
        sts = boto3.client("sts", region_name=AWS_REGION)
        assumed = sts.assume_role(
            RoleArn=body["client_role_arn"],
            RoleSessionName=f"CP-{client_id}-{int(datetime.utcnow().timestamp())}",
            DurationSeconds=3600
        )
        creds = assumed["Credentials"]

        session = boto3.Session(
            aws_access_key_id=creds["AccessKeyId"],
            aws_secret_access_key=creds["SecretAccessKey"],
            aws_session_token=creds["SessionToken"]
        )
        client_s3 = session.client("s3")
        obj = client_s3.get_object(
            Bucket=body["source_bucket"],
            Key=body["source_key"]
        )
        data_bytes = obj["Body"].read()

        dest_key = (
            f"clients/{client_id}/uploads/"
            f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_"
            f"{body['source_key'].split('/')[-1]}"
        )
        cp_s3 = boto3.client("s3", region_name=AWS_REGION)
        cp_s3.put_object(Bucket=CP_S3_BUCKET, Key=dest_key, Body=data_bytes)

        return jsonify({
            "success": True,
            "message": "Data pulled via assumed cross-account role",
            "assumed_role": body["client_role_arn"],
            "dest_key": dest_key,
            "dest_bucket": CP_S3_BUCKET,
            "bytes_ingested": len(data_bytes)
        }), 200

    except botocore.exceptions.ClientError as e:
        code = e.response["Error"]["Code"]
        return jsonify({
            "success": False,
            "error": f"STS/S3 error [{code}]: {str(e)}"
        }), 403
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
