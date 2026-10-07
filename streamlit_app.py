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
        r = requests.post(f"{get_api_url()}{path}", json=payload, timeout=30)
        return r.json() if r.ok else {"error": f"HTTP {r.status_code}: {r.text}"}
    except Exception as e:
        return {"error": str(e)}

if "kg_messages" not in st.session_state:
    st.session_state.kg_messages = []

# --- Premium Clean CSS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
html, body, [class*="css"], [class*="st-"] {
    font-family: 'Inter', sans-serif !important;
}
/* Hide top chrome */
header { visibility: hidden !important; background: transparent !important; }
footer { display: none !important; }
.stDeployButton { display: none !important; }

.main, .block-container {
    background: transparent !important;
}

/* Refine chat input */
[data-testid="stChatInput"] {
    padding-bottom: 24px;
}

/* Beautiful Fade-In Animation for Cards */
@keyframes fadeUp {
    0% { opacity: 0; transform: translateY(15px); }
    100% { opacity: 1; transform: translateY(0); }
}

/* Chat Message Styling */
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

[data-testid="stChatMessageAvatarUser"] {
    background-color: transparent !important;
}
[data-testid="stChatMessageAvatarAssistant"] {
    background-color: transparent !important;
}
</style>
""", unsafe_allow_html=True)

def set_bg():
    st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.3), rgba(0,0,0,0.7)), url(/assets/hero_bg.png);
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }
    </style>
    """, unsafe_allow_html=True)

set_bg()

# Render the sidebar for configuration
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
                        st.success(f"✅ Ingested {data.get('ingested', 0)} episodes")
                    else:
                        st.error(f"Failed: {resp.text}")
                except Exception as e:
                    progress.empty()
                    st.error(f"Error: {e}")
        
st.write("<br>", unsafe_allow_html=True)

def get_svg_avatar(role):
    path = f"assets/user.svg" if role == "user" else f"assets/ai.svg"
    try:
        with open(path, "r") as f:
            svg = f.read()
            return f"data:image/svg+xml;base64,{base64.b64encode(svg.encode()).decode()}"
    except:
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
            st.session_state.kg_messages.append({
                "role": "assistant",
                "content": reply
            })
