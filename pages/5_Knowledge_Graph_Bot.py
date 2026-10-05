import streamlit as st
import requests
import os
import re

st.set_page_config(
    page_title="AI Knowledge Assistant",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Hide ALL Streamlit chrome — sidebar, menu, footer, header ─────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');

/* Hide everything Streamlit */
#MainMenu, header, footer, [data-testid="stSidebar"],
[data-testid="collapsedControl"], .stDeployButton { display: none !important; }

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
    background: #f5f5f5 !important;
}

/* Full viewport layout */
.main .block-container {
    padding: 0 !important;
    max-width: 100% !important;
}

/* App shell */
.chat-shell {
    display: flex;
    flex-direction: column;
    height: 100vh;
    max-width: 760px;
    margin: 0 auto;
    background: #ffffff;
    box-shadow: 0 0 40px rgba(0,0,0,0.08);
}

/* Top bar */
.chat-topbar {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 16px 20px;
    background: #ffffff;
    border-bottom: 1px solid #ebebeb;
    position: sticky;
    top: 0;
    z-index: 100;
}

.chat-avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    color: white;
    font-weight: 700;
    flex-shrink: 0;
}

.chat-title { font-size: 1rem; font-weight: 600; color: #111; margin: 0; }
.chat-status { font-size: 0.75rem; color: #22c55e; margin: 0; }

/* Chat message bubbles */
.msg-row {
    display: flex;
    padding: 6px 20px;
    gap: 10px;
    align-items: flex-end;
}
.msg-row.user { flex-direction: row-reverse; }

.msg-bubble {
    max-width: 75%;
    padding: 10px 14px;
    border-radius: 18px;
    font-size: 0.9rem;
    line-height: 1.5;
    word-wrap: break-word;
}
.msg-bubble.assistant {
    background: #f2f2f7;
    color: #111;
    border-bottom-left-radius: 4px;
}
.msg-bubble.user {
    background: #6366f1;
    color: #fff;
    border-bottom-right-radius: 4px;
}

.msg-tag {
    display: inline-block;
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.05em;
    padding: 2px 8px;
    border-radius: 10px;
    margin-bottom: 5px;
}
.tag-stored { background: #dcfce7; color: #166534; }
.tag-query  { background: #dbeafe; color: #1e40af; }
.tag-error  { background: #fee2e2; color: #991b1b; }

/* Input area */
[data-testid="stChatInput"] {
    border: 1.5px solid #e0e0e0 !important;
    border-radius: 24px !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06) !important;
    background: #fff !important;
    padding: 4px 8px !important;
    font-size: 0.9rem !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color: #6366f1 !important;
    box-shadow: 0 2px 12px rgba(99,102,241,0.15) !important;
}

/* Padding for messages area */
.messages-area { padding: 12px 0 8px; }
</style>
""", unsafe_allow_html=True)

# ── Top bar ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="chat-topbar">
    <div class="chat-avatar">K</div>
    <div>
        <div class="chat-title">Knowledge Assistant</div>
        <div class="chat-status">● Active</div>
    </div>
</div>
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

INGEST_RE = re.compile(
    r"^(remember\s+that|add\s+(fact|info|data)[:\s]+|note\s+that|store|save|learn\s+that)\s*",
    re.IGNORECASE,
)

# ── Session state ─────────────────────────────────────────────────────────────
if "kg_messages" not in st.session_state:
    st.session_state.kg_messages = [
        {"role": "assistant", "content": "Hi! Ask me anything or say **remember that...** to teach me a new fact.", "intent": None}
    ]

# ── Render messages ───────────────────────────────────────────────────────────
st.markdown('<div class="messages-area">', unsafe_allow_html=True)

for msg in st.session_state.kg_messages:
    role = msg["role"]
    intent = msg.get("intent")
    content = msg["content"]

    tag_html = ""
    if intent == "ingest":
        tag_html = '<span class="msg-tag tag-stored">STORED</span><br>'
    elif intent == "query":
        tag_html = '<span class="msg-tag tag-query">RESULT</span><br>'
    elif intent == "error":
        tag_html = '<span class="msg-tag tag-error">ERROR</span><br>'

    st.markdown(f"""
    <div class="msg-row {role}">
        <div class="msg-bubble {role}">{tag_html}{content}</div>
    </div>
    """, unsafe_allow_html=True)

    # Show result cards inline if available
    if msg.get("results"):
        for r in msg["results"][:3]:
            score = f"{r['score']:.2f}" if r.get("score") is not None else "–"
            fact = r.get("fact", str(r))
            st.markdown(f"""
            <div class="msg-row assistant">
                <div class="msg-bubble assistant" style="font-size:0.8rem;background:#f8f8ff;border:1px solid #e0e0ff;">
                    {fact} &nbsp;<span style="color:#888;font-size:0.7rem">({score})</span>
                </div>
            </div>""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ── Chat input ────────────────────────────────────────────────────────────────
user_input = st.chat_input("Message Knowledge Assistant...")

if user_input:
    st.session_state.kg_messages.append({"role": "user", "content": user_input, "intent": None})

    with st.spinner(""):
        response = graphiti_post("/api/chat", {"message": user_input})

    if "error" in response:
        st.session_state.kg_messages.append({
            "role": "assistant",
            "content": f"Something went wrong. Please try again.",
            "intent": "error",
        })
    else:
        intent = response.get("intent", "query")
        reply  = response.get("reply", "No response.")
        results = response.get("results") if intent == "query" else None
        st.session_state.kg_messages.append({
            "role": "assistant",
            "content": reply,
            "intent": intent,
            "results": results,
        })

    st.rerun()
