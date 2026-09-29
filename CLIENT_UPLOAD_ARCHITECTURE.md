# Client Data Upload — Workflow, Methods & AWS Key Architecture

This document covers **Point 3** from the original spec:  
> *"Methods that how client can upload a sample data to our CP (our cloud/AWS layer) with their custom keys / client keys"*

---

## Overview

When a client (another company) wants to send their data into your Context Platform, there are **3 methods** depending on their setup. All 3 are implemented in [api/upload_routes.py](./api/upload_routes.py).

---

## Method 1 — Presigned S3 URL (Recommended / Simplest)

> Client does **NOT** need any AWS credentials. Your platform generates a time-limited upload URL.

### Flow

```
Client                          Your Platform (CP)                   AWS S3
  │                                     │                               │
  │  POST /api/v1/uploads/              │                               │
  │  presigned-url                      │                               │
  │  { client_id, filename }  ────────▶ │                               │
  │                                     │── boto3.generate_presigned ──▶│
  │                                     │◀── presigned PUT URL ─────────│
  │◀── { presigned_url, object_key } ───│                               │
  │                                     │                               │
  │── HTTP PUT (file bytes) ────────────────────────────────────────── ▶│
  │   (no AWS keys, URL is the auth)    │                               │
  │◀── 200 OK ──────────────────────────────────────────────────────── │
  │                                     │                               │
  │  POST /api/v1/context/upload        │                               │
  │  { client_id, context_type, data }──▶ (CP processes + stores) ──────│
```

### What the client does

```bash
# Step 1: Get presigned URL from CP
curl -X POST https://your-cp-url/api/v1/uploads/presigned-url \
  -H "Content-Type: application/json" \
  -d '{"client_id": "client_abc", "filename": "products.csv"}'

# Response:
# { "presigned_url": "https://s3.amazonaws.com/context-platform-uploads/clients/client_abc/...", ... }

# Step 2: PUT file directly to S3 using presigned URL (no AWS keys needed)
curl -X PUT "<presigned_url>" \
  -H "Content-Type: text/csv" \
  --data-binary @products.csv
```

### AWS Setup (your side only)
- Your platform's IAM role needs `s3:PutObject` on `context-platform-uploads` bucket
- Set bucket policy to allow pre-signed PUTs from your role
- URL expires in 1 hour by default (configurable)

---

## Method 2 — Client Provides Their Own AWS Keys

> Client generates a short-lived IAM key pair and passes it to CP. CP reads from **client's** S3 bucket.

### Flow

```
Client AWS Account              Your Platform (CP)                   AWS S3
  │                                     │                               │
  │ Client generates:                   │                               │
  │  - AWS Access Key ID                │                               │
  │  - AWS Secret Access Key            │                               │
  │  - (Optional) Session Token         │                               │
  │                                     │                               │
  │  POST /api/v1/uploads/              │                               │
  │  via-client-keys                    │                               │
  │  { client_id,                       │                               │
  │    aws_access_key_id,    ─────────▶ │                               │
  │    aws_secret_access_key,           │── boto3.Session(client_creds)▶│
  │    source_bucket,                   │── s3.get_object() ───────────▶│ (client's bucket)
  │    source_key }                     │◀── file bytes ────────────────│
  │                                     │── s3.put_object() ───────────▶│ (CP bucket)
  │◀── { success, bytes_ingested } ─────│                               │
```

### What the client does

```bash
# Client creates a scoped IAM user/role with read-only S3 access
# then calls CP with their temp credentials:

curl -X POST https://your-cp-url/api/v1/uploads/via-client-keys \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "client_abc",
    "aws_access_key_id": "AKIAIOSFODNN7EXAMPLE",
    "aws_secret_access_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
    "aws_session_token": "AQoDYXdzEJr...",
    "source_bucket": "acme-corp-data",
    "source_key": "exports/products_oct2024.csv",
    "aws_region": "us-east-1"
  }'
```

### Security considerations

| Risk | Mitigation |
|---|---|
| Client shares long-lived keys | ⚠️ Recommend STS temporary credentials only |
| Keys in HTTP body | Use HTTPS (EB has SSL) — never log request body |
| Over-permissive keys | CP only calls `s3:GetObject` on source — document this to client |
| Key rotation | Keys should expire within 1 hour (STS session token) |

---

## Method 3 — Cross-Account IAM Role (Most Secure / Enterprise)

> Client creates an IAM role in THEIR AWS account that trusts YOUR account. No keys are ever shared.

### One-time setup (client does this once)

```json
// Client creates IAM Role: "CPAccessRole" in their AWS account
// Trust Policy (allows your AWS account to assume this role):
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::YOUR_AWS_ACCOUNT_ID:root"
      },
      "Action": "sts:AssumeRole",
      "Condition": {
        "StringEquals": {
          "sts:ExternalId": "CP-client_abc"
        }
      }
    }
  ]
}

// Permission Policy (attached to the same role):
{
  "Effect": "Allow",
  "Action": ["s3:GetObject", "s3:ListBucket"],
  "Resource": [
    "arn:aws:s3:::acme-corp-data",
    "arn:aws:s3:::acme-corp-data/*"
  ]
}
```

### Flow

```
Client AWS Account              Your Platform (CP)              AWS STS
  │                                     │                          │
  │ Shares only:                        │                          │
  │  - Role ARN                         │                          │
  │  - Source bucket/key  ────────────▶ │                          │
  │                                     │── sts.assume_role() ───▶ │
  │                                     │◀── temp credentials ───── │
  │                                     │    (15min - 1hr)          │
  │                                     │                          │
  │                                     │── s3.get_object() ──────▶ (client's bucket, using temp creds)
  │                                     │◀── file bytes ────────────│
  │                                     │── s3.put_object() ───────▶ (CP bucket, using CP creds)
  │◀── { success, bytes_ingested } ─────│
```

### What the client does

```bash
# Client shares only their Role ARN and source location:
curl -X POST https://your-cp-url/api/v1/uploads/assume-role \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "client_abc",
    "client_role_arn": "arn:aws:iam::123456789012:role/CPAccessRole",
    "source_bucket": "acme-corp-data",
    "source_key": "exports/products_oct2024.csv"
  }'
```

---

## Comparison Table

| | Method 1 (Presigned URL) | Method 2 (Client Keys) | Method 3 (Cross-account Role) |
|---|---|---|---|
| **Client needs AWS?** | ❌ No | ✅ Yes | ✅ Yes (one-time setup) |
| **Keys shared with CP?** | ❌ Never | ⚠️ Yes (temp only) | ❌ Never |
| **Setup complexity** | 🟢 Simple | 🟡 Medium | 🔴 One-time IAM setup |
| **Security level** | 🟡 Good | 🟡 OK (temp creds) | 🟢 Best |
| **Best for** | Quick onboarding | Internal/trusted clients | Enterprise / Production |
| **API endpoint** | `POST /uploads/presigned-url` | `POST /uploads/via-client-keys` | `POST /uploads/assume-role` |

---

## Recommended Onboarding Flow

```
New Client Signs Up
       │
       ▼
POST /api/v1/clients/register
{ name, email, aws_account_id, plan }
       │
       ▼
CP returns client_id
       │
       ├─── Quick Start (Method 1) ──────────────────────────────────────▶
       │     Client calls /presigned-url, PUTs file, done.
       │
       └─── Enterprise (Method 3) ────────────────────────────────────────▶
             CP sends client the IAM trust policy template.
             Client creates role in their account.
             Client shares role ARN with CP.
             CP calls /assume-role to pull data on demand.
```

---

## Future: S3 Event Trigger → Auto-Ingest

Once data lands in the CP S3 bucket (via any method above):

```
Client upload lands in S3
       │
       ▼
S3 Event Notification → Lambda
       │
       ▼
Lambda parses file (CSV / JSON / Parquet)
       │
       ▼
Lambda calls POST /api/v1/context/upload
       │
       ▼
Context Platform stores structured data
       │
       ▼
AI Agents query CP and take action
```

This closes the full loop:  
**Client uploads → Context Platform ingests → AI Agents act on it.**
