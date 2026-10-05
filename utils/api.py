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
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Main Content Container */
    .main .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

def render_sidebar_api_config():
    inject_global_css()
    with st.sidebar:
        st.markdown("""
        <div style="padding: 8px 0 12px 0; margin-bottom: 8px; border-bottom: 1px solid #334155;">
            <div style="font-size: 1.2rem; font-weight: 800; color: #ffffff; letter-spacing: -0.01em;">ContextOS</div>
        </div>
        """, unsafe_allow_html=True)
        # We now rely exclusively on environment variables for API routing rather than UI inputs.
