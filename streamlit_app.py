import streamlit as st
import requests
import os
import base64
from datetime import datetime
from utils.api import render_sidebar_api_config

st.set_page_config(
    page_title="Knowledge OS",
    layout="wide",
    initial_sidebar_state="expanded",
)

def get_api_url():
    return os.environ.get("GRAPHITI_API_URL", "http://localhost:8080")

def graphiti_post(path, payload):
    try:
        r = requests.post(f"{get_api_url()}{path}", json=payload, timeout=60)
        return r.json() if r.ok else {"error": f"HTTP {r.status_code}: {r.text}"}
    except Exception as e:
        return {"error": str(e)}

def graphiti_get(path):
    try:
        r = requests.get(f"{get_api_url()}{path}", timeout=5)
        return r.json() if r.ok else {}
    except Exception:
        return {}

if "kg_messages" not in st.session_state:
    st.session_state.kg_messages = []
if "demo_questions" not in st.session_state:
    st.session_state.demo_questions = []
if "demo_loaded_sector" not in st.session_state:
    st.session_state.demo_loaded_sector = None

# --- Premium Clean CSS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
html, body, [class*="css"], [class*="st-"] {
    font-family: 'Inter', sans-serif !important;
}
header { visibility: hidden !important; background: transparent !important; }
footer { display: none !important; }
.stDeployButton { display: none !important; }
.main, .block-container { background: transparent !important; }

[data-testid="stChatInput"] { padding-bottom: 24px; }

@keyframes fadeUp {
    0% { opacity: 0; transform: translateY(15px); }
    100% { opacity: 1; transform: translateY(0); }
}

.stChatMessage {
    background: rgba(20, 20, 20, 0.4) !important;
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 12px;
    padding: 1rem !important;
    margin-bottom: 1rem !important;
    color: #ffffff !important;
}

[data-testid="stChatMessageAvatarUser"] { background-color: transparent !important; }
[data-testid="stChatMessageAvatarAssistant"] { background-color: transparent !important; }

.demo-question-btn {
    display: inline-block;
    background: rgba(59, 130, 246, 0.15);
    border: 1px solid rgba(96, 165, 250, 0.4);
    color: #93c5fd;
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 0.82rem;
    margin: 4px 4px 4px 0;
    cursor: pointer;
    transition: all 0.2s ease;
}
.demo-question-btn:hover {
    background: rgba(59, 130, 246, 0.35);
    color: #ffffff;
}
.sector-badge {
    display: inline-block;
    background: linear-gradient(90deg, #3b82f6, #8b5cf6);
    color: #fff;
    padding: 3px 12px;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 600;
    margin-bottom: 8px;
}
</style>
""", unsafe_allow_html=True)

@st.cache_data(show_spinner=False)
def _encode_bg():
    """Only used locally — on production nginx serves /assets/ directly."""
    import base64, os
    img_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "hero_bg.png")
    try:
        with open(img_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception:
        return None

def set_bg():
    is_production = os.environ.get("STREAMLIT_ENV") == "production"
    if is_production:
        # nginx serves /assets/ directly — no WebSocket overhead
        bg_css = "url('/assets/hero_bg.png')"
    else:
        b64 = _encode_bg()
        bg_css = f"url('data:image/png;base64,{b64}')" if b64 else \
                 "linear-gradient(135deg, #0a0a1a 0%, #0f172a 40%, #1a0a2e 70%, #0a0a1a 100%)"

    st.markdown(f"""
    <style>
    .stApp {{
        background: linear-gradient(rgba(0,0,0,0.45), rgba(0,0,0,0.75)), {bg_css};
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    </style>
    """, unsafe_allow_html=True)

set_bg()
render_sidebar_api_config()

if "daily_quote" not in st.session_state:
    import random
    quotes = [
        "The goal is to turn data into information, and information into insight.",
        "Knowledge is the only wealth that grows when you share it.",
        "An investment in knowledge pays the best interest.",
        "Connecting the dots to see the bigger picture.",
        "Every piece of data tells a story."
    ]
    st.session_state.daily_quote = random.choice(quotes)

st.write("<br><br>", unsafe_allow_html=True)
hour = datetime.now().hour
greeting = "Good Morning" if hour < 12 else ("Good Afternoon" if hour < 17 else "Good Evening")

st.markdown(f"<h1 style='text-align: center; font-weight: 500; letter-spacing: -0.02em; color: #ffffff;'>{greeting}</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; color: #d1d5db; font-weight: 300; font-size: 1.05rem; margin-bottom: 40px;'><i>\"{st.session_state.daily_quote}\"</i></p>", unsafe_allow_html=True)

# ── Top cards ────────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)
with col1:
    with st.container(border=True, height=180):
        st.markdown("### Store Knowledge")
        st.write("Teach the bot facts directly so it remembers them forever.")
        st.caption("*Example: 'Remember that Acme Corp is a premium client.'*")

with col2:
    with st.container(border=True, height=180):
        st.markdown("### Query Graph")
        st.write("Ask complex relational questions about your ingested data.")
        st.caption("*Example: 'What projects is Alice working on?'*")

st.write("<br>", unsafe_allow_html=True)

# ── Demo Sector Loader ───────────────────────────────────────────────────────
with st.container(border=True):
    st.markdown("### Try a Live Demo")
    st.write("Select an industry sector. The AI will load real, interconnected sample data and suggest questions to show graph accuracy.")
    st.write("")

    # Fetch available sectors from the backend
    sector_data = graphiti_get("/api/demo-sectors")
    sector_list  = sector_data.get("sectors", [])
    sector_names = [s["name"] for s in sector_list]
    sector_descs = {s["name"]: s["description"] for s in sector_list}

    if not sector_names:
        sector_names = ["Finance & Banking", "Healthcare & Pharma", "Retail & E-Commerce", "Logistics & Supply Chain"]

    col_drop, col_btn = st.columns([3, 1])
    with col_drop:
        selected_sector = st.selectbox(
            "Choose a sector",
            options=sector_names,
            format_func=lambda x: f"{x}  —  {sector_descs.get(x, '')}",
            label_visibility="collapsed",
            key="sector_dropdown"
        )
    with col_btn:
        load_clicked = st.button("Load Demo Data", type="primary", use_container_width=True, key="load_demo_btn")

    if load_clicked and selected_sector:
        with st.spinner(f"Loading {selected_sector} data into Knowledge Graph..."):
            result = graphiti_post("/api/load-demo-data", {"sector": selected_sector})
        if "error" in result:
            st.error(f"Failed: {result['error']}")
        else:
            ingested = result.get("ingested", 0)
            total    = result.get("total_facts", 0)
            st.success(f"Loaded {ingested} of {total} facts for **{selected_sector}** into the Knowledge Graph.")
            st.session_state.demo_questions    = result.get("questions", [])
            st.session_state.demo_loaded_sector = selected_sector

    # Show suggested questions as clickable chips
    if st.session_state.demo_questions:
        st.markdown(f"<div class='sector-badge'>{st.session_state.demo_loaded_sector}</div>", unsafe_allow_html=True)
        st.markdown("**Try these questions — click any to ask instantly:**")
        cols = st.columns(2)
        for i, q in enumerate(st.session_state.demo_questions):
            with cols[i % 2]:
                if st.button(q, key=f"demo_q_{i}", use_container_width=True):
                    # Inject the question into chat and process immediately
                    st.session_state.kg_messages.append({"role": "user", "content": q})
                    with st.spinner("🔍 Searching the Knowledge Graph..."):
                        response = graphiti_post("/api/chat", {"message": q})
                    if "error" in response:
                        st.session_state.kg_messages.append({
                            "role": "assistant",
                            "content": f"⚠️ {response['error']}"
                        })
                    else:
                        st.session_state.kg_messages.append({
                            "role": "assistant",
                            "content": response.get("reply", "Done.")
                        })
                    st.rerun()

st.write("<br>", unsafe_allow_html=True)

# ── File Upload ──────────────────────────────────────────────────────────────
with st.container(border=True):
    st.markdown("### Upload & Ingest a File")
    st.write("Upload a CSV or PDF and it will be automatically ingested into the Knowledge Graph.")
    st.write("")
    uploaded = st.file_uploader(
        "Drag & drop a file here",
        type=["csv", "pdf"],
        label_visibility="collapsed",
        key="kg_file_upload"
    )
    if uploaded:
        col_info, col_btn = st.columns([3, 1])
        with col_info:
            st.markdown(f"**Selected:** `{uploaded.name}` — `{uploaded.size / 1024:.1f} KB`")
        with col_btn:
            if st.button("Ingest into Graph", type="primary", use_container_width=True):
                file_bytes = uploaded.read()
                progress = st.progress(0, text="Uploading to Graph...")
                try:
                    import requests as req
                    resp = req.post(
                        f"{get_api_url()}/api/ingest-file",
                        files={"file": (uploaded.name, file_bytes, uploaded.type)},
                        timeout=120
                    )
                    progress.progress(100, text="Done!")
                    if resp.ok:
                        data = resp.json()
                        st.success(f"Ingested {data.get('ingested', 0)} episodes from {uploaded.name}")
                    else:
                        st.error(f"Failed: {resp.text}")
                except Exception as e:
                    progress.empty()
                    st.error(f"Error: {e}")

st.write("<br>", unsafe_allow_html=True)

# ── Chat ─────────────────────────────────────────────────────────────────────
def get_svg_avatar(role):
    return "🧑‍💻" if role == "user" else "✨"

for msg in st.session_state.kg_messages:
    with st.chat_message(msg["role"], avatar=get_svg_avatar(msg["role"])):
        st.markdown(msg["content"])

if user_input := st.chat_input("Ask a question, or type 'Remember that...' to store a new fact."):
    st.session_state.kg_messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar=get_svg_avatar("user")):
        st.markdown(user_input)

    with st.chat_message("assistant", avatar=get_svg_avatar("assistant")):
        with st.spinner("Processing..."):
            response = graphiti_post("/api/chat", {"message": user_input})

        if "error" in response:
            error_msg = f"Failed to connect: {response['error']}"
            st.error(error_msg)
            st.session_state.kg_messages.append({"role": "assistant", "content": error_msg})
        else:
            reply = response.get("reply", "Done.")
            st.markdown(reply)
            st.session_state.kg_messages.append({"role": "assistant", "content": reply})
