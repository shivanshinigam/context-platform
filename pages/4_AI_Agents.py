import streamlit as st
from utils.api import api_get, api_post, render_sidebar_api_config

st.set_page_config(page_title="AI Agents - Context Platform", layout="wide")
render_sidebar_api_config()

# ── Sleek Dark Enterprise Header ──
st.markdown("""
<div style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); color: #ffffff; padding: 28px 36px; border-radius: 16px; margin-bottom: 24px; box-shadow: 0 10px 30px rgba(15, 23, 42, 0.12); border: 1px solid #334155;">
    <div style="display: inline-block; background: rgba(59, 130, 246, 0.2); color: #60a5fa; padding: 5px 14px; border-radius: 20px; font-size: 0.75rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 10px; border: 1px solid rgba(96, 165, 250, 0.3);">
        STEP 4 OF 4 | AI AGENT JOBS
    </div>
    <div style="font-size: 2rem; font-weight: 800; margin-bottom: 8px; letter-spacing: -0.02em; color: #f8fafc;">
        Autonomous AI Agent Control Panel
    </div>
    <div style="font-size: 0.98rem; color: #94a3b8; line-height: 1.6; max-width: 880px;">
        Orchestrate AI agents (Data Enrichment, Anomaly Detection, Recommendations, Summarization) against
        ingested client context payloads. Monitor async job processing and view generated intelligence.
    </div>
</div>
""", unsafe_allow_html=True)

# ── Navigation Buttons ──
n_col1, n_col2 = st.columns([4, 1])
with n_col2:
    st.page_link("pages/5_Dashboard.py", label="Proceed to Operations Dashboard →", use_container_width=True)

st.write("")

tab_trigger, tab_jobs = st.tabs(["Launch Agent Job", "Job Monitor & Telemetry"])

with tab_trigger:
    with st.container(border=True):
        st.subheader("Launch New AI Agent Job")
        st.caption("Target an ingested context payload and execute AI model tasks.")
        st.write("")
        
        types_data = api_get("/api/v1/agents/types")
        agent_types = types_data.get("agent_types", [
            "data_enrichment", "anomaly_detection", "recommendation",
            "summarization", "classification", "sentiment_analysis"
        ])

        col1, col2 = st.columns(2)
        with col1:
            client_id = st.text_input(
                "Client ID *",
                placeholder="e.g. client_d307b5c989b8",
                key="ag_client_id"
            )
            context_id = st.text_input(
                "Context ID *",
                placeholder="Paste context_id from Step 3 (Context Store)",
                key="ag_context_id"
            )
        with col2:
            agent_type = st.selectbox(
                "AI Agent Model / Service",
                [t.replace("_", " ").title() for t in agent_types],
                key="ag_type"
            )
            agent_type_raw = agent_types[[t.replace("_", " ").title() for t in agent_types].index(agent_type)]

        with st.expander("Agent Parameters & Hyperparameters"):
            col_cfg1, col_cfg2 = st.columns(2)
            with col_cfg1:
                top_k = st.number_input("top_k (Recommendations count)", min_value=1, max_value=100, value=5, key="ag_topk")
            with col_cfg2:
                threshold = st.slider("Confidence / Anomaly Threshold", 0.0, 1.0, 0.8, step=0.05, key="ag_threshold")

        st.write("")
        if st.button("Trigger Agent Execution", key="btn_trigger", type="primary"):
            if not client_id or not context_id:
                st.error("Client ID and Context ID are required")
            else:
                payload = {
                    "client_id": client_id,
                    "context_id": context_id,
                    "agent_type": agent_type_raw,
                    "config": {
                        "top_k": top_k,
                        "threshold": threshold
                    }
                }
                with st.spinner(f"Queuing {agent_type} agent job..."):
                    result = api_post("/api/v1/agents/trigger", payload)

                if result.get("success"):
                    st.success(f"Agent job queued successfully! Job ID: `{result['job_id']}`")
                    st.info("Switch to the **Job Monitor & Telemetry** tab above to view results!")
                else:
                    st.error(f"{result.get('error', 'Trigger failed')}")

with tab_jobs:
    st.subheader("Real-Time Job Telemetry")
    
    f1, f2, f3 = st.columns([2, 2, 1])
    with f1:
        filter_client = st.text_input("Filter by Client ID", key="job_filter_client")
    with f2:
        filter_status = st.selectbox(
            "Filter by Job Status",
            ["All", "queued", "running", "completed", "failed"],
            key="job_filter_status"
        )
    with f3:
        st.write("")
        st.write("")
        if st.button("Refresh Telemetry", key="job_refresh", use_container_width=True):
            st.rerun()

    params = {}
    if filter_client:
        params["client_id"] = filter_client
    if filter_status != "All":
        params["status"] = filter_status

    data = api_get("/api/v1/agents/jobs", params)
    jobs = data.get("jobs", [])

    st.markdown(f"**Total Agent Workloads Found:** `{len(jobs)}`")
    st.write("")

    if not jobs:
        st.info("No agent jobs executed yet. Launch an agent job in the left tab!")
    else:
        for j in jobs[::-1]:
            status = j.get("status", "queued")
            badge_cls = "badge-running" if status in ["queued", "running"] else "badge-active"
            res = j.get("result", {})
            
            with st.expander(f"{j.get('agent_type','').replace('_',' ').title()} — Job ID: {j.get('job_id','')} ({status.upper()})"):
                col_a, col_b = st.columns([2, 1])
                with col_a:
                    st.markdown(f"**Job ID:** `{j.get('job_id')}`")
                    st.markdown(f"**Client ID:** `{j.get('client_id')}`")
                    st.markdown(f"**Target Context ID:** `{j.get('context_id','')}`")
                    st.markdown(f"**Status:** <span class='{badge_cls}'>{status.upper()}</span>", unsafe_allow_html=True)
                    st.caption(f"Created: {j.get('created_at','')[:19]} UTC")

                with col_b:
                    if st.button("Poll Status", key=f"poll_{j['job_id']}"):
                        fresh = api_get(f"/api/v1/agents/status/{j['job_id']}")
                        if fresh.get("success"):
                            st.rerun()
                        else:
                            st.error(fresh.get("error"))

                st.write("")
                st.divider()

                if res:
                    st.markdown("### AI Agent Intelligence Generated")
                    
                    if "executive_summary" in res:
                        st.info(f"**Executive Summary:**\n\n{res['executive_summary']}")
                        if "key_insights" in res:
                            st.markdown("**Key Strategic Insights:**")
                            for insight in res["key_insights"]:
                                st.markdown(f"- {insight}")

                    elif "recommended_actions" in res:
                        st.markdown("**Recommended Business Actions:**")
                        for act in res["recommended_actions"]:
                            st.markdown(f"- **{act}**")
                        if "top_recommendations" in res:
                            st.markdown("**Top SKU Recommendations:**")
                            rec_cols = st.columns(len(res["top_recommendations"]))
                            for idx, rec in enumerate(res["top_recommendations"]):
                                with rec_cols[idx]:
                                    with st.container(border=True):
                                        st.markdown(f"**#{rec.get('rank')} {rec.get('name')}**")
                                        st.caption(f"SKU: {rec.get('sku')}")
                                        st.metric("Predicted Lift", rec.get('predicted_lift'))

                    elif "flagged_anomalies" in res:
                        st.warning(f"**{res.get('anomalies_detected', 0)} Anomalies Detected**")
                        for item in res["flagged_anomalies"]:
                            with st.container(border=True):
                                st.markdown(f"**{item.get('type')}** on `{item.get('item_id')}` — Severity: `{item.get('severity')}`")
                                st.write(item.get('details'))

                    elif "enriched_fields" in res:
                        st.success(f"**Enriched {res.get('records_enriched', 0)} Records!** Data Quality: `{res.get('data_quality_score')}`")
                        st.write(f"Added metadata fields: `{', '.join(res.get('enriched_fields', []))}`")

                    with st.expander("Inspect Raw AI Agent JSON Response"):
                        st.json(j)

                elif status == "running":
                    st.info("Agent model computation in progress...")
                elif status == "queued":
                    st.info("Queued in execution pipeline...")
