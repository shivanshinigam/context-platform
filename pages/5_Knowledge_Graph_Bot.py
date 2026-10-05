import streamlit as st
import requests
import os
import re

st.set_page_config(
    page_title="Knowledge Assistant",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── ChatGPT-style Light UI ────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

/* Hide Streamlit top header and footer, but KEEP sidebar */
header { visibility: hidden; }
footer { display: none !important; }
.stDeployButton { display: none !important; }

/* Main app background */
.stApp {
    background-color: #ffffff;
    font-family: 'Inter', sans-serif;
}

/* Override default padding to maximize chat space */
.main .block-container {
    padding-top: 2rem !important;
    padding-bottom: 0 !important;
    max-width: 850px !important;
    margin: 0 auto;
}

/* ── CHAT MESSAGES ── */
.chat-container {
    padding-bottom: 120px; /* space for input */
    display: flex;
    flex-direction: column;
    gap: 24px;
}

.msg-row {
    display: flex;
    width: 100%;
    gap: 16px;
}
.msg-row.user {
    justify-content: flex-end;
}
.msg-row.assistant {
    justify-content: flex-start;
}

/* Avatars */
.avatar {
    width: 32px;
    height: 32px;
    border-radius: 4px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    font-size: 14px;
    flex-shrink: 0;
}
.avatar-bot {
    background-color: #10a37f;
    color: white;
}

/* Bubbles */
.bubble {
    max-width: 75%;
    font-size: 0.95rem;
    line-height: 1.6;
    color: #0d0d0d;
}
.bubble.user {
    background-color: #f4f4f4;
    padding: 10px 16px;
    border-radius: 16px;
    border-bottom-right-radius: 4px;
}
.bubble.assistant {
    padding: 4px 0;
}

/* Tags for knowledge ops */
.tag {
    display: inline-block;
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    padding: 2px 6px;
    border-radius: 4px;
    margin-bottom: 6px;
    text-transform: uppercase;
}
.tag-stored { background: #dcfce7; color: #166534; }
.tag-result { background: #f3f4f6; color: #374151; }
.tag-error  { background: #fee2e2; color: #991b1b; }

/* ── INPUT AREA ── */
.input-container {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: linear-gradient(180deg, rgba(255,255,255,0) 0%, #ffffff 25%);
    padding: 24px 0 32px;
    display: flex;
    justify-content: center;
    z-index: 100;
}

[data-testid="stChatInput"] {
    max-width: 800px;
    margin: 0 auto;
}
[data-testid="stChatInput"] > div {
    border: 1px solid #e5e5e5 !important;
    border-radius: 16px !important;
    background-color: #ffffff !important;
    box-shadow: 0 0 15px rgba(0,0,0,0.05) !important;
}
[data-testid="stChatInput"] > div:focus-within {
    border-color: #10a37f !important;
}
[data-testid="stChatInput"] textarea {
    font-size: 1rem !important;
}

/* Sidebar styling overrides if needed to match */
[data-testid="stSidebar"] {
    background-color: #f9f9f9;
}
</style>
""", unsafe_allow_html=True)

# ── Helpers ───────────────────────────────────────────────────────────────────
def get_api_url():
    return os.environ.get("GRAPHITI_API_URL", "http://localhost:8080")

def graphiti_post(path, payload):
    try:
        r = requests.post(f"{get_api_url()}{path}", json=payload, timeout=30)
        return r.json() if r.ok else {"error": f"HTTP {r.status_code}: {r.text}"}
    except Exception as e:
        return {"error": str(e)}

# ── Session state ─────────────────────────────────────────────────────────────
if "kg_messages" not in st.session_state:
    st.session_state.kg_messages = [
        {"role": "assistant", "content": "Hello! I'm your Knowledge Graph Assistant. Ask me anything, or teach me a new fact by saying *'remember that...'*", "intent": None}
    ]

# ── Render messages ───────────────────────────────────────────────────────────
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

for msg in st.session_state.kg_messages:
    role = msg["role"]
    intent = msg.get("intent")
    content = msg["content"]

    if role == "user":
        st.markdown(f"""
        <div class="msg-row user">
            <div class="bubble user">{content}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        tag_html = ""
        if intent == "ingest":
            tag_html = '<div class="tag tag-stored">Stored to Graph</div>'
        elif intent == "query":
            tag_html = '<div class="tag tag-result">Graph Result</div>'
        elif intent == "error":
            tag_html = '<div class="tag tag-error">Error</div>'

        st.markdown(f"""
        <div class="msg-row assistant">
            <div class="avatar avatar-bot">AI</div>
            <div class="bubble assistant">
                {tag_html}
                <div style="margin-top:2px">{content}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if msg.get("results"):
            for r in msg["results"][:3]:
                score = f"{r['score']:.2f}" if r.get("score") is not None else "–"
                fact = r.get("fact", str(r))
                st.markdown(f"""
                <div class="msg-row assistant">
                    <div class="avatar" style="background:transparent"></div>
                    <div class="bubble assistant" style="font-size:0.85rem; color:#666; border-left: 2px solid #e5e5e5; padding-left: 12px;">
                        {fact} <span style="font-size:0.7rem; color:#aaa;">({score})</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ── Input ─────────────────────────────────────────────────────────────────────
# We use Streamlit's native chat input, styled via CSS
user_input = st.chat_input("Message Knowledge Assistant...")

if user_input:
    st.session_state.kg_messages.append({"role": "user", "content": user_input, "intent": None})

    with st.spinner("Thinking..."):
        response = graphiti_post("/api/chat", {"message": user_input})

    if "error" in response:
        st.session_state.kg_messages.append({
            "role": "assistant",
            "content": f"Something went wrong. Please try again.",
            "intent": "error",
        })
    else:
        intent = response.get("intent", "query")
        reply = response.get("reply", "No response.")
        results = response.get("results") if intent == "query" else None
        st.session_state.kg_messages.append({
            "role": "assistant",
            "content": reply,
            "intent": intent,
            "results": results,
        })

    st.rerun()
