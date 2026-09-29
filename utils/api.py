import os
import streamlit as st
import requests

def get_api_base() -> str:
    default_url = os.environ.get("FLASK_API_URL", "http://localhost:5001")
    return st.session_state.get("api_url", default_url)

def api_get(path: str, params: dict = None) -> dict:
    try:
        r = requests.get(f"{get_api_base()}{path}", params=params, timeout=5)
        return r.json() if r.ok else {"success": False, "error": f"HTTP {r.status_code}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def api_post(path: str, payload: dict) -> dict:
    try:
        r = requests.post(f"{get_api_base()}{path}", json=payload, timeout=15)
        return r.json() if r.ok else {"success": False, "error": f"HTTP {r.status_code}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def api_post_file(path: str, client_id: str, file_name: str, file_bytes: bytes, content_type: str = None) -> dict:
    try:
        files = {"file": (file_name, file_bytes, content_type or "application/octet-stream")}
        data = {"client_id": client_id}
        r = requests.post(f"{get_api_base()}{path}", data=data, files=files, timeout=30)
        return r.json() if r.ok else {"success": False, "error": f"HTTP {r.status_code}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def api_delete(path: str) -> dict:
    try:
        r = requests.delete(f"{get_api_base()}{path}", timeout=5)
        return r.json() if r.ok else {"success": False, "error": f"HTTP {r.status_code}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def api_patch(path: str, payload: dict) -> dict:
    try:
        r = requests.patch(f"{get_api_base()}{path}", json=payload, timeout=5)
        return r.json() if r.ok else {"success": False, "error": f"HTTP {r.status_code}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def inject_global_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    /* Compact Non-Zoomed Base Font & Density */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-size: 14px !important;
    }
    
    /* Main Content Container */
    .main .block-container {
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: 1400px !important;
    }

    /* ── Cohesive Light Sidebar (Matching White Content Layout) ── */
    section[data-testid="stSidebar"],
    [data-testid="stSidebarContent"],
    [data-testid="stSidebar"] {
        background-color: #f8fafc !important;
        background: #f8fafc !important;
        border-right: 1px solid #e2e8f0 !important;
    }
    
    section[data-testid="stSidebar"] *,
    [data-testid="stSidebarContent"] * {
        color: #475569 !important;
        font-size: 13px !important;
    }
    
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] strong,
    [data-testid="stSidebarContent"] h1,
    [data-testid="stSidebarContent"] h2,
    [data-testid="stSidebarContent"] h3,
    [data-testid="stSidebarContent"] strong {
        color: #0f172a !important;
    }

    /* Sidebar Inputs & Controls */
    section[data-testid="stSidebar"] input,
    [data-testid="stSidebarContent"] input {
        background-color: #ffffff !important;
        background: #ffffff !important;
        color: #0f172a !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 8px !important;
    }
    section[data-testid="stSidebar"] input:focus,
    [data-testid="stSidebarContent"] input:focus {
        border-color: #2563eb !important;
        box-shadow: 0 0 0 1px #2563eb !important;
    }
    section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p,
    [data-testid="stSidebarContent"] [data-testid="stWidgetLabel"] p {
        color: #475569 !important;
        font-weight: 600 !important;
    }
    section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p,
    [data-testid="stSidebarContent"] [data-testid="stCaptionContainer"] p {
        color: #64748b !important;
        font-weight: 600 !important;
    }

    /* Sidebar Navigation Links */
    [data-testid="stSidebarNav"] ul li a {
        padding: 7px 12px !important;
        border-radius: 8px !important;
        margin: 2px 4px !important;
        transition: all 0.15s ease-in-out !important;
        background: transparent !important;
        border: 1px solid transparent !important;
    }

    [data-testid="stSidebarNav"] ul li a:hover {
        background-color: #f1f5f9 !important;
        border-color: #cbd5e1 !important;
    }
    
    [data-testid="stSidebarNav"] ul li a:hover span {
        color: #0f172a !important;
    }

    /* Active Sidebar Nav Item */
    [data-testid="stSidebarNav"] ul li a[aria-current="page"] {
        background: #eff6ff !important;
        border: 1px solid #bfdbfe !important;
        box-shadow: 0 2px 6px rgba(37, 99, 235, 0.08) !important;
    }

    [data-testid="stSidebarNav"] ul li a[aria-current="page"] span {
        color: #2563eb !important;
        font-weight: 700 !important;
    }

    /* ── Animated Sidebar Collapse Tooltip Badge ── */
    [data-testid="stSidebarCollapseButton"] {
        position: relative !important;
    }
    [data-testid="stSidebarCollapseButton"]::after {
        content: "Close Sidebar";
        position: absolute;
        left: 36px;
        top: 50%;
        transform: translateY(-50%);
        background: #2563eb;
        color: #ffffff !important;
        font-size: 11px !important;
        font-weight: 700 !important;
        padding: 4px 10px;
        border-radius: 6px;
        white-space: nowrap;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.4);
        pointer-events: none;
        animation: fadeOutSidebarTooltip 3.5s forwards ease-in-out;
    }

    @keyframes fadeOutSidebarTooltip {
        0% { opacity: 0; transform: translateY(-50%) translateX(-6px); }
        20% { opacity: 1; transform: translateY(-50%) translateX(0px); }
        75% { opacity: 1; transform: translateY(-50%) translateX(0px); }
        100% { opacity: 0; transform: translateY(-50%) translateX(6px); visibility: hidden; }
    }

    /* Compact Buttons */
    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
        border: none !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        border-radius: 8px !important;
        padding: 0.4rem 1.1rem !important;
        box-shadow: 0 3px 10px rgba(37, 99, 235, 0.2) !important;
        transition: all 0.15s ease-in-out !important;
    }
    div.stButton > button[kind="primary"]:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 5px 15px rgba(37, 99, 235, 0.3) !important;
    }
    div.stButton > button:not([kind="primary"]) {
        border-radius: 8px !important;
        border: 1px solid #cbd5e1 !important;
        background: #ffffff !important;
        color: #1e293b !important;
        font-weight: 500 !important;
        font-size: 13px !important;
        padding: 0.4rem 1rem !important;
        transition: all 0.15s ease-in-out !important;
    }
    div.stButton > button:not([kind="primary"]):hover {
        border-color: #2563eb !important;
        color: #2563eb !important;
        background: #f0f9ff !important;
    }
    
    /* Compact Tabs Bar */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px !important;
        border-bottom: 2px solid #e2e8f0 !important;
        padding-bottom: 2px !important;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 8px 16px !important;
        border-radius: 6px 6px 0 0 !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        color: #64748b !important;
        background: transparent !important;
        border: none !important;
    }
    .stTabs [aria-selected="true"] {
        color: #2563eb !important;
        background: #eff6ff !important;
        border-bottom: 2px solid #2563eb !important;
    }
    
    /* Compact Metrics */
    [data-testid="stMetricValue"] {
        font-size: 1.6rem !important;
        font-weight: 800 !important;
        color: #0f172a !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 12px !important;
        color: #64748b !important;
    }
    [data-testid="stMetric"] {
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        padding: 12px 16px !important;
        border-radius: 10px !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.02) !important;
    }

    /* Expanders Header */
    .streamlit-expanderHeader {
        font-weight: 600 !important;
        font-size: 13px !important;
        color: #0f172a !important;
        border-radius: 8px !important;
        background: #f8fafc !important;
        border: 1px solid #e2e8f0 !important;
        padding: 10px 14px !important;
    }

    /* Status Badges */
    .badge-active {
        background: #dcfce7;
        color: #166534;
        padding: 3px 10px;
        border-radius: 16px;
        font-size: 0.7rem;
        font-weight: 700;
    }
    .badge-running {
        background: #dbeafe;
        color: #1e40af;
        padding: 3px 10px;
        border-radius: 16px;
        font-size: 0.7rem;
        font-weight: 700;
    }
    </style>
    """, unsafe_allow_html=True)

def render_sidebar_api_config():
    inject_global_css()
    with st.sidebar:
        st.markdown("""
        <div style="padding: 8px 0 12px 0; margin-bottom: 8px; border-bottom: 1px solid #e2e8f0;">
            <div style="font-size: 1.2rem; font-weight: 800; color: #0f172a; letter-spacing: -0.01em;">ContextOS</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)
        st.caption("Backend Status")
        default_api = os.environ.get("FLASK_API_URL", "http://localhost:5001")
        api_url = st.text_input(
            "Flask API Base URL",
            value=st.session_state.get("api_url", default_api),
            help="Backend Flask server endpoint."
        )
        if api_url:
            st.session_state["api_url"] = api_url

