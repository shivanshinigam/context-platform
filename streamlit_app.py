import streamlit as st
from utils.api import render_sidebar_api_config

st.set_page_config(
    page_title="ContextOS - AI Agent Platform",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Inject Custom Landing Page CSS ──
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@200;300;400;500;600&display=swap');

/* Reset and apply Montserrat */
html, body, [class*="css"] {
    font-family: 'Montserrat', sans-serif !important;
}

/* Remove default Streamlit top padding to allow full-bleed hero */
.block-container {
    padding-top: 0rem !important;
    padding-bottom: 2rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    max-width: 100% !important;
}

/* Hero Section */
.hero-section {
    position: relative;
    width: 100%;
    height: 55vh;
    background: url(/assets/hero_bg.png) no-repeat center center;
    background-size: cover;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    color: white;
    margin-bottom: 2rem;
}

/* Dark overlay for readability */
.hero-overlay {{
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background: rgba(0, 0, 0, 0.45);
    z-index: 1;
}}

.hero-content {{
    position: relative;
    z-index: 2;
    padding: 20px;
}}

.hero-title {{
    font-size: 3.2rem;
    font-weight: 300;
    letter-spacing: 0.3em;
    margin-bottom: 12px;
    text-transform: uppercase;
}}

.hero-subtitle {{
    font-size: 1.05rem;
    font-weight: 300;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: rgba(255, 255, 255, 0.85);
}}

/* Workflow Step Pill */
.step-pill {{
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    background: #e0e7ff;
    color: #3730a3;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    margin-bottom: 8px;
    text-transform: uppercase;
}}
</style>
""", unsafe_allow_html=True)

# ── Render Hero Section ──
st.markdown("""
<div class="hero-section">
    <div class="hero-overlay"></div>
    <div class="hero-content">
        <div class="hero-title">Context OS</div>
        <div class="hero-subtitle">Enterprise Platform for Ingesting Context & Orchestrating AI Agents</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Interactive Platform Workflow Guide ──
st.subheader("Platform Architecture & End-to-End Workflow")
st.caption("ContextOS bridges enterprise client data with specialized AI agents through a secure 4-step pipeline:")

w1, w2, w3, w4 = st.columns(4)

with w1:
    with st.container(border=True):
        st.markdown('<span class="step-pill">STEP 1</span>', unsafe_allow_html=True)
        st.markdown("**1. Client Onboarding**")
        st.write("Register enterprise clients, specify industry domains, and set up cross-account AWS IAM roles.")
        st.page_link("pages/1_Clients.py", label="Go to Clients →", use_container_width=True)

with w2:
    with st.container(border=True):
        st.markdown('<span class="step-pill">STEP 2</span>', unsafe_allow_html=True)
        st.markdown("**2. Secure Data Upload**")
        st.write("Ingest client data via Presigned URLs, STS keys, or zero-trust Cross-Account S3 Role Assumption.")
        st.page_link("pages/2_Data_Upload.py", label="Go to Data Upload →", use_container_width=True)

with w3:
    with st.container(border=True):
        st.markdown('<span class="step-pill">STEP 3</span>', unsafe_allow_html=True)
        st.markdown("**3. Context Store**")
        st.write("Browse, query, or manually inject structured context objects tagged by client and category.")
        st.page_link("pages/3_Context_Store.py", label="Go to Context Store →", use_container_width=True)

with w4:
    with st.container(border=True):
        st.markdown('<span class="step-pill">STEP 4</span>', unsafe_allow_html=True)
        st.markdown("**4. AI Agent Jobs**")
        st.write("Run AI agents (Enrichment, Anomaly Detection, Recommendations) against context & monitor results.")
        st.page_link("pages/4_AI_Agents.py", label="Go to AI Agents →", use_container_width=True)

st.write("")
st.divider()

# ── Quick Dashboard Banner ──
c_dash1, c_dash2 = st.columns([3, 1])
with c_dash1:
    st.markdown("### Platform Operations & Live Metrics")
    st.write("Monitor live operational metrics, active agent jobs, and recent context ingestion events across all clients.")
with c_dash2:
    st.write("")
    st.page_link("pages/5_Dashboard.py", label="Open Operations Dashboard →", use_container_width=True)

# Render the sidebar
render_sidebar_api_config()


