import json
import streamlit as st
from utils.api import api_get, api_post, api_delete, render_sidebar_api_config

st.set_page_config(page_title="Context Store - Context Platform", layout="wide")
render_sidebar_api_config()

# ── Sleek Dark Enterprise Header ──
st.markdown("""
<div style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); color: #ffffff; padding: 28px 36px; border-radius: 16px; margin-bottom: 24px; box-shadow: 0 10px 30px rgba(15, 23, 42, 0.12); border: 1px solid #334155;">
    <div style="display: inline-block; background: rgba(59, 130, 246, 0.2); color: #60a5fa; padding: 5px 14px; border-radius: 20px; font-size: 0.75rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 10px; border: 1px solid rgba(96, 165, 250, 0.3);">
        STEP 3 OF 4 | KNOWLEDGE VIEWER
    </div>
    <div style="font-size: 2rem; font-weight: 800; margin-bottom: 8px; letter-spacing: -0.02em; color: #f8fafc;">
        Knowledge Viewer
    </div>
    <div style="font-size: 0.98rem; color: #94a3b8; line-height: 1.6; max-width: 880px;">
        Look inside the AI's brain. See the exact facts and documents it has successfully learned for each private company.
    </div>
</div>
""", unsafe_allow_html=True)

# ── Navigation Buttons ──
n_col1, n_col2 = st.columns([4, 1])
with n_col2:
    st.page_link("pages/4_AI_Agents.py", label="Proceed to AI Agents →", use_container_width=True)

st.write("")

tab_browse, tab_upload = st.tabs(["Browse Context Store", "Manual Context Injection"])

with tab_browse:
    st.subheader("Context Store Queries")
    
    f1, f2, f3 = st.columns([2, 2, 1])
    with f1:
        filter_client = st.text_input("Filter by Client ID", key="ctx_filter_client")
    with f2:
        filter_type = st.text_input("Filter by Context Type", key="ctx_filter_type")
    with f3:
        st.write("")
        st.write("")
        refresh = st.button("Refresh Results", key="ctx_refresh", use_container_width=True)

    params = {}
    if filter_client:
        params["client_id"] = filter_client
    if filter_type:
        params["type"] = filter_type

    data = api_get("/api/v1/context/list", params)
    entries = data.get("context_entries", [])

    st.markdown(f"**Context Entries Found:** `{len(entries)}`")
    st.write("")

    if not entries:
        st.info("No context entries stored yet. Ingest a dataset in Step 2 (Data Upload) or inject one manually below.")
    else:
        for e in entries[::-1]:
            with st.expander(f"{e.get('context_type','').replace('_',' ').title()} — ID: {e.get('context_id','')}"):
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    st.markdown(f"**Context ID:** `{e.get('context_id')}`")
                    st.markdown(f"**Client ID:** `{e.get('client_id')}`")
                    st.markdown(f"**Category / Tags:** `{', '.join(e.get('tags', [])) or 'None'}`")
                    st.markdown(f"**Ingested:** `{e.get('created_at','')[:19]} UTC`")
                    st.markdown("**Structured Data:**")
                    st.json(e.get("data", {}))
                with col_b:
                    if st.button("Delete Context", key=f"del_{e['context_id']}"):
                        res = api_delete(f"/api/v1/context/{e['context_id']}")
                        if res.get("success"):
                            st.success("Entry removed!")
                            st.rerun()
                        else:
                            st.error(res.get("error", "Delete failed"))

with tab_upload:
    with st.container(border=True):
        st.subheader("Manual Context Injection")
        st.caption("Construct and inject a raw JSON payload directly into the platform.")

        col1, col2 = st.columns(2)
        with col1:
            client_id = st.text_input("Client ID *", placeholder="e.g. client_d307b5c989b8", key="ctx_client_id")
            context_type = st.selectbox(
                "Context Type",
                ["product_catalog", "user_profile", "transaction_history",
                 "customer_segment", "inventory", "custom"],
                key="ctx_type"
            )
        with col2:
            tags_input = st.text_input("Tags (comma-separated)", placeholder="e.g. retail, electronics", key="ctx_tags")
            aws_region = st.selectbox("AWS Region", ["us-east-1", "us-west-2", "ap-south-1", "eu-west-1"], key="ctx_region")

        data_input = st.text_area(
            "Payload Content (JSON) *",
            height=160,
            placeholder='{\n  "store_name": "Downtown Retail",\n  "items": [{"id": 1, "name": "Widget", "price": 99.99}]\n}',
            key="ctx_data"
        )

        st.write("")
        if st.button("Inject Context Payload", key="btn_upload_ctx", type="primary"):
            if not client_id:
                st.error("Client ID is required")
            elif not data_input.strip():
                st.error("JSON payload content is required")
            else:
                try:
                    parsed_data = json.loads(data_input)
                except json.JSONDecodeError as err:
                    st.error(f"Invalid JSON syntax: {err}")
                    st.stop()

                tags = [t.strip() for t in tags_input.split(",") if t.strip()]
                payload = {
                    "client_id": client_id,
                    "context_type": context_type,
                    "data": parsed_data,
                    "tags": tags,
                    "aws_region": aws_region
                }

                with st.spinner("Injecting payload..."):
                    result = api_post("/api/v1/context/upload", payload)

                if result.get("success"):
                    st.success(f"Context payload injected! ID: `{result['context_id']}`")
                    st.json(result["entry"])
                else:
                    st.error(f"Injection failed: {result.get('error', 'Unknown error')}")
