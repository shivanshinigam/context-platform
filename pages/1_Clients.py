import streamlit as st
from utils.api import api_get, api_post, api_patch, render_sidebar_api_config

st.set_page_config(page_title="Clients - Context Platform", layout="wide")
render_sidebar_api_config()

# ── Sleek Dark Enterprise Header ──
st.markdown("""
<div style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); color: #ffffff; padding: 28px 36px; border-radius: 16px; margin-bottom: 24px; box-shadow: 0 10px 30px rgba(15, 23, 42, 0.12); border: 1px solid #334155;">
    <div style="display: inline-block; background: rgba(59, 130, 246, 0.2); color: #60a5fa; padding: 5px 14px; border-radius: 20px; font-size: 0.75rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 10px; border: 1px solid rgba(96, 165, 250, 0.3);">
        STEP 1 OF 4 | CLIENT ONBOARDING
    </div>
    <div style="font-size: 2rem; font-weight: 800; margin-bottom: 8px; letter-spacing: -0.02em; color: #f8fafc;">
        Client Directory
    </div>
    <div style="font-size: 0.98rem; color: #94a3b8; line-height: 1.6; max-width: 880px;">
        Create a private workspace for each company. This guarantees strict data separation—so Company A's documents never mix with Company B's documents.
    </div>
</div>
""", unsafe_allow_html=True)

# ── Navigation Buttons ──
n_col1, n_col2 = st.columns([4, 1])
with n_col2:
    st.page_link("pages/2_Data_Upload.py", label="Proceed to Data Upload →", use_container_width=True)

st.write("")

tab_register, tab_list = st.tabs(["Register New Client", "All Registered Clients"])

with tab_register:
    with st.container(border=True):
        st.subheader("Client Onboarding Form")
        st.caption("Enter client organization details and AWS account metadata.")
        st.write("")

        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Company / Client Name *", placeholder="e.g. Acme Retail Solutions")
            email = st.text_input("Contact Email *", placeholder="e.g. admin@acme.com")
            industry = st.selectbox(
                "Industry Domain",
                ["retail", "ecommerce", "healthcare", "finance", "logistics", "manufacturing", "other"]
            )
        with col2:
            aws_account_id = st.text_input(
                "Client AWS Account ID",
                placeholder="e.g. 123456789012",
                help="12-digit AWS account number used for STS AssumeRole"
            )
            aws_region = st.selectbox("Primary AWS Region", ["us-east-1", "us-west-2", "ap-south-1", "eu-west-1"])
            plan = st.selectbox("Service Plan / Tier", ["starter", "pro", "enterprise"])

        st.write("")
        if st.button("Register Client", type="primary"):
            if not name or not email:
                st.error("Client Name and Email are required")
            else:
                payload = {
                    "name": name,
                    "email": email,
                    "industry": industry,
                    "aws_account_id": aws_account_id,
                    "aws_region": aws_region,
                    "plan": plan
                }
                with st.spinner("Registering client..."):
                    result = api_post("/api/v1/clients/register", payload)

                if result.get("success"):
                    st.success(f"Client registered! Assigned ID: `{result['client_id']}`")
                    with st.expander("View Registered Client Record"):
                        st.json(result["client"])
                else:
                    st.error(f"{result.get('error', 'Registration failed')}")

with tab_list:
    col_title, col_btn = st.columns([4, 1])
    with col_title:
        st.subheader("Active Client Roster")
    with col_btn:
        if st.button("Refresh List", use_container_width=True):
            st.rerun()
    
    data = api_get("/api/v1/clients/")
    clients = data.get("clients", [])

    st.markdown(f"**Total Registered Clients:** `{len(clients)}`")
    st.write("")

    if not clients:
        st.info("No clients registered yet. Use the 'Register New Client' tab above to get started.")
    else:
        for c in clients[::-1]:
            status = c.get("status", "active")
            with st.expander(f"{c.get('name','Unknown')} — ID: {c.get('client_id','')} ({status.upper()})"):
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    st.markdown(f"**Contact Email:** `{c.get('email')}`")
                    st.markdown(f"**Industry Domain:** `{c.get('industry','').title()}`")
                    st.markdown(f"**Service Tier:** `{c.get('plan','').title()}`")
                    st.markdown(f"**AWS Account ID:** `{c.get('aws_account_id') or 'N/A'}` | **Region:** `{c.get('aws_region') or 'us-east-1'}`")
                    st.markdown(f"**Status:** <span class='badge-active'>{status.upper()}</span>", unsafe_allow_html=True)
                with col_b:
                    new_status = st.selectbox(
                        "Update Status",
                        ["active", "inactive", "suspended"],
                        key=f"status_{c['client_id']}",
                        index=["active", "inactive", "suspended"].index(status)
                    )
                    if st.button("Save Status", key=f"upd_{c['client_id']}"):
                        res = api_patch(
                            f"/api/v1/clients/{c['client_id']}/status",
                            {"status": new_status}
                        )
                        if res.get("success"):
                            st.success("Status updated!")
                            st.rerun()
                        else:
                            st.error(res.get("error", "Failed to update"))
