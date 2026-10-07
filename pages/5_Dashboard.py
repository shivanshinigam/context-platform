import streamlit as st
from utils.api import api_get, render_sidebar_api_config

st.set_page_config(page_title="Dashboard - Context Platform", layout="wide")
render_sidebar_api_config()

# ── Sleek Dark Enterprise Header ──
st.markdown("""
<div style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); color: #ffffff; padding: 28px 36px; border-radius: 16px; margin-bottom: 24px; box-shadow: 0 10px 30px rgba(15, 23, 42, 0.12); border: 1px solid #334155;">
    <div style="display: inline-block; background: rgba(59, 130, 246, 0.2); color: #60a5fa; padding: 5px 14px; border-radius: 20px; font-size: 0.75rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 10px; border: 1px solid rgba(96, 165, 250, 0.3);">
        SYSTEM OVERVIEW
    </div>
    <div style="font-size: 2rem; font-weight: 800; margin-bottom: 8px; letter-spacing: -0.02em; color: #f8fafc;">
        Platform Dashboard
    </div>
    <div style="font-size: 0.98rem; color: #94a3b8; line-height: 1.6; max-width: 880px;">
        See a simple, real-time summary of all your active clients, uploaded documents, 
        and finished AI tasks at a glance.
    </div>
</div>
""", unsafe_allow_html=True)

# ── Live stats ──
context_data = api_get("/api/v1/context/list")
client_data  = api_get("/api/v1/clients/")
jobs_data    = api_get("/api/v1/agents/jobs")

context_count = context_data.get("count", 0)
client_count  = client_data.get("count", 0)
jobs_count    = jobs_data.get("count", 0)
running_jobs  = len([j for j in jobs_data.get("jobs", []) if j.get("status") in ["running", "queued"]])

# ── Metric row ──
st.subheader("Platform Telemetry")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Registered Clients", client_count, help="Step 1: Onboarded Clients")
c2.metric("Context Store Objects", context_count, help="Step 3: Context Objects")
c3.metric("Total AI Agent Jobs", jobs_count, help="Step 4: Agent Jobs Executed")
c4.metric("Active Workloads", running_jobs, help="Currently processing AI jobs")

st.write("")
st.divider()

# ── Recent Activity ──
col1, col2 = st.columns(2)

with col1:
    st.subheader("Recent Context Ingestion Activity")
    st.caption("Latest payloads ingested into ContextOS")
    entries = context_data.get("context_entries", [])
    if entries:
        for e in entries[-5:][::-1]:
            with st.container(border=True):
                st.markdown(f"**Type:** `{e.get('context_type', 'unknown').replace('_', ' ').title()}`")
                st.markdown(f"**Context ID:** `{e.get('context_id','')}`")
                st.markdown(f"**Client ID:** `{e.get('client_id','')}`")
                st.caption(f"Uploaded: {e.get('created_at','')[:19]} UTC")
    else:
        st.info("No context entries stored yet.")

with col2:
    st.subheader("Recent Agent Workloads")
    st.caption("Latest AI agent execution jobs")
    jobs = jobs_data.get("jobs", [])
    if jobs:
        for j in jobs[-5:][::-1]:
            status = j.get("status", "queued")
            badge_cls = "badge-running" if status in ["queued", "running"] else "badge-active"
            with st.container(border=True):
                st.markdown(f"**Model:** `{j.get('agent_type','').replace('_', ' ').title()}`")
                st.markdown(f"**Job ID:** `{j.get('job_id','')}`")
                st.markdown(f"**Client ID:** `{j.get('client_id','')}`")
                st.markdown(f"**Status:** <span class='{badge_cls}'>{status.upper()}</span>", unsafe_allow_html=True)
                st.caption(f"Created: {j.get('created_at','')[:19]} UTC")
    else:
        st.info("No agent jobs executed yet.")

st.write("")
if st.button("Refresh Operational Telemetry", type="primary"):
    st.rerun()
