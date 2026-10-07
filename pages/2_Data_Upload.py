import json
import streamlit as st
from utils.api import api_post, api_post_file, render_sidebar_api_config

st.set_page_config(page_title="Data Upload - Context Platform", layout="wide")
render_sidebar_api_config()

# ── Compact Sleek Dark Header ──
st.markdown("""
<div style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); color: #ffffff; padding: 18px 24px; border-radius: 12px; margin-bottom: 16px; box-shadow: 0 4px 16px rgba(15, 23, 42, 0.08); border: 1px solid #334155;">
    <div style="display: inline-block; background: rgba(59, 130, 246, 0.2); color: #60a5fa; padding: 3px 10px; border-radius: 16px; font-size: 0.7rem; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 6px; border: 1px solid rgba(96, 165, 250, 0.3);">
        STEP 2 OF 4 | DATA UPLOAD
    </div>
    <div style="font-size: 2rem; font-weight: 800; margin-bottom: 8px; letter-spacing: -0.02em; color: #f8fafc;">
        Upload Files
    </div>
    <div style="font-size: 0.98rem; color: #94a3b8; line-height: 1.6; max-width: 880px;">
        Connect a company's database directly to the AI. Instead of uploading files one by one, thousands of documents can sync automatically in the background overnight.
    </div>
</div>
""", unsafe_allow_html=True)

# ── Navigation Buttons ──
n_col1, n_col2 = st.columns([4, 1])
with n_col2:
    st.page_link("pages/3_Context_Store.py", label="Proceed to Context Store →", use_container_width=True)

st.write("")

# ── Tabs ──
tab0, tab1, tab2, tab3 = st.tabs([
    "Direct File Upload (Drag & Drop)",
    "Presigned S3 URL",
    "Temporary AWS Keys",
    "Cross-Account IAM Role"
])

# ─────────────────────────────────────────────
# Tab 0 — Direct File Upload
# ─────────────────────────────────────────────
with tab0:
    with st.container(border=True):
        st.subheader("Direct File Upload (Drag & Drop)")
        st.caption("Upload sample CSV, JSON, TXT, or PDF datasets directly from your local computer into the Context Store.")
        
        st.write("")
        c1, c2 = st.columns([1, 2])
        with c1:
            direct_client_id = st.text_input("Client ID *", placeholder="e.g. client_d307b5c989b8", key="dir_cid")
        with c2:
            uploaded_file = st.file_uploader(
                "Choose a file to ingest",
                type=["csv", "json", "txt", "pdf", "xlsx"],
                key="dir_file_input"
            )

        st.write("")
        if st.button("Upload File to Context Platform", key="btn_direct_upload", type="primary"):
            if not direct_client_id:
                st.error("Client ID is required")
            elif not uploaded_file:
                st.error("Please select a file to upload")
            else:
                file_bytes = uploaded_file.read()
                with st.spinner(f"Ingesting '{uploaded_file.name}' into ContextOS..."):
                    result = api_post_file(
                        "/api/v1/uploads/direct",
                        client_id=direct_client_id,
                        file_name=uploaded_file.name,
                        file_bytes=file_bytes,
                        content_type=uploaded_file.type
                    )

                if result.get("success"):
                    st.success(f"File '{uploaded_file.name}' ingested successfully!")
                    st.markdown(f"**Generated Context ID:** `{result.get('context_id')}`")
                    st.markdown(f"**File Size:** `{result.get('bytes_received', 0):,} bytes`")
                    if result.get("context_entry"):
                        with st.expander("View Parsed Context Payload"):
                            st.json(result["context_entry"])
                else:
                    st.error(f"Upload failed: {result.get('error', 'Unknown error')}")

# ─────────────────────────────────────────────
# Tab 1 — Presigned URL
# ─────────────────────────────────────────────
with tab1:
    with st.container(border=True):
        st.subheader("Generate Presigned S3 Upload URL")
        st.caption("Generate a time-limited S3 upload URL. The client needs no AWS IAM credentials to send files.")

        col1, col2 = st.columns(2)
        with col1:
            m1_client_id = st.text_input("Client ID *", placeholder="e.g. client_abc123", key="m1_cid")
            m1_filename  = st.text_input("Filename", value="sales_report.csv", key="m1_fname")
        with col2:
            m1_content_type = st.selectbox(
                "Content Type",
                ["text/csv", "application/json", "application/octet-stream"],
                key="m1_ctype"
            )
            m1_expiry = st.number_input("URL Expiry (seconds)", value=3600, min_value=60, max_value=86400, key="m1_expiry")

        st.write("")
        if st.button("Generate S3 Presigned URL", key="btn_m1", type="primary"):
            if not m1_client_id:
                st.error("Client ID is required")
            else:
                with st.spinner("Generating presigned URL..."):
                    result = api_post("/api/v1/uploads/presigned-url", {
                        "client_id": m1_client_id,
                        "filename": m1_filename,
                        "content_type": m1_content_type,
                        "expiry_seconds": m1_expiry
                    })

                if result.get("success"):
                    st.success("Presigned S3 URL generated!")
                    st.code(result.get("presigned_url", ""), language="text")
                    st.markdown("**Client cURL upload example:**")
                    st.code(
                        f'curl -X PUT "{result.get("presigned_url", "")}" \\\n'
                        f'  -H "Content-Type: {m1_content_type}" \\\n'
                        f'  --data-binary @{m1_filename}',
                        language="bash"
                    )
                else:
                    st.error(f"{result.get('error', 'Unknown error')}")

# ─────────────────────────────────────────────
# Tab 2 — Client AWS Keys
# ─────────────────────────────────────────────
with tab2:
    with st.container(border=True):
        st.subheader("Pull Data via Temporary AWS Keys")
        st.caption("Provide temporary client STS credentials to transfer files from the client's S3 bucket into ContextOS.")

        col1, col2 = st.columns(2)
        with col1:
            m2_client_id   = st.text_input("Client ID *", placeholder="e.g. client_abc123", key="m2_cid")
            m2_access_key  = st.text_input("AWS Access Key ID *", placeholder="ASIA...", key="m2_ak", type="password")
            m2_secret_key  = st.text_input("AWS Secret Access Key *", placeholder="...", key="m2_sk", type="password")
            m2_session_tok = st.text_input("STS Session Token", placeholder="AQoD...", key="m2_tok", type="password")
        with col2:
            m2_src_bucket  = st.text_input("Client S3 Bucket *", placeholder="acme-corp-data", key="m2_bucket")
            m2_src_key     = st.text_input("Source Object Key *", placeholder="exports/products.csv", key="m2_key")
            m2_region      = st.selectbox("AWS Region", ["us-east-1", "us-west-2", "ap-south-1", "eu-west-1"], key="m2_region")

        st.write("")
        if st.button("Pull Data with Client Keys", key="btn_m2", type="primary"):
            missing = [f for f, v in {
                "Client ID": m2_client_id, "Access Key": m2_access_key,
                "Secret Key": m2_secret_key, "Source Bucket": m2_src_bucket,
                "Source Key": m2_src_key
            }.items() if not v]

            if missing:
                st.error(f"Missing required fields: {', '.join(missing)}")
            else:
                with st.spinner("Pulling data from client S3 bucket..."):
                    result = api_post("/api/v1/uploads/via-client-keys", {
                        "client_id": m2_client_id,
                        "aws_access_key_id": m2_access_key,
                        "aws_secret_access_key": m2_secret_key,
                        "aws_session_token": m2_session_tok or None,
                        "source_bucket": m2_src_bucket,
                        "source_key": m2_src_key,
                        "aws_region": m2_region
                    })

                if result.get("success"):
                    st.success(f"Ingested {result.get('bytes_ingested', 0):,} bytes into ContextOS!")
                    st.markdown(f"**Destination Path:** `{result.get('dest_key')}`")
                else:
                    st.error(f"{result.get('error', 'Unknown error')}")

# ─────────────────────────────────────────────
# Tab 3 — Cross-Account Role
# ─────────────────────────────────────────────
with tab3:
    with st.container(border=True):
        st.subheader("Pull Data via Cross-Account IAM Role")
        st.caption("Zero credential sharing. ContextOS assumes the client's IAM role using AWS STS AssumeRole.")

        col1, col2 = st.columns(2)
        with col1:
            m3_client_id   = st.text_input("Client ID *", placeholder="e.g. client_abc123", key="m3_cid")
            m3_role_arn    = st.text_input("Client IAM Role ARN *", placeholder="arn:aws:iam::123456789012:role/CPAccessRole", key="m3_arn")
        with col2:
            m3_src_bucket  = st.text_input("Client S3 Bucket *", placeholder="acme-corp-data", key="m3_bucket")
            m3_src_key     = st.text_input("Object Key *", placeholder="exports/products.csv", key="m3_key")

        with st.expander("View IAM Policy Templates"):
            st.markdown("**Role Trust Policy:**")
            st.code(json.dumps({
                "Version": "2012-10-17",
                "Statement": [{
                    "Effect": "Allow",
                    "Principal": {"AWS": "arn:aws:iam::YOUR_CP_ACCOUNT_ID:root"},
                    "Action": "sts:AssumeRole",
                    "Condition": {"StringEquals": {"sts:ExternalId": f"CP-{m3_client_id or 'CLIENT_ID'}"}}
                }]
            }, indent=2), language="json")

        st.write("")
        if st.button("Pull Data via Assumed Role", key="btn_m3", type="primary"):
            missing = [f for f, v in {
                "Client ID": m3_client_id, "Role ARN": m3_role_arn,
                "Source Bucket": m3_src_bucket, "Source Key": m3_src_key
            }.items() if not v]

            if missing:
                st.error(f"Missing required fields: {', '.join(missing)}")
            else:
                with st.spinner("Assuming cross-account role..."):
                    result = api_post("/api/v1/uploads/assume-role", {
                        "client_id": m3_client_id,
                        "client_role_arn": m3_role_arn,
                        "source_bucket": m3_src_bucket,
                        "source_key": m3_src_key
                    })

                if result.get("success"):
                    st.success(f"Assumed role successfully! {result.get('bytes_ingested', 0):,} bytes ingested.")
                    st.markdown(f"**Stored Destination:** `{result.get('dest_key')}`")
                else:
                    st.error(f"{result.get('error', 'Unknown error')}")
