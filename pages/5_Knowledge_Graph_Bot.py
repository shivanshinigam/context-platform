import streamlit as st
import requests
import os
from utils.api import render_sidebar_api_config

st.set_page_config(page_title="Knowledge Graph Bot - Context Platform", layout="wide")
render_sidebar_api_config()

# ── Top Navigation ─────────────────────────────────────────────────────────────
st.page_link("pages/4_AI_Agents.py", label="← Back to AI Agent Control Panel")

# ── Custom CSS for a beautiful, clean light-mode UI ──
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

/* Premium Light Header */
.premium-header {
    background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
    padding: 20px 30px;
    border-radius: 16px;
    margin-bottom: 10px;
    box-shadow: 0 10px 40px rgba(37, 99, 235, 0.05);
    border: 1px solid #e2e8f0;
    position: relative;
    overflow: hidden;
}

.header-badge {
    display: inline-block;
    background: #eff6ff;
    color: #2563eb;
    padding: 6px 16px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 15px;
    border: 1px solid #bfdbfe;
}

.header-title {
    font-size: 2.6rem;
    font-weight: 800;
    margin-bottom: 10px;
    letter-spacing: -0.02em;
    color: #0f172a;
}

.header-desc {
    font-size: 1.1rem;
    color: #475569;
    line-height: 1.6;
    max-width: 800px;
}

/* Chat Message Bubbles */
[data-testid="stChatMessage"] {
    padding: 1.2rem 1.5rem !important;
    border-radius: 16px !important;
    margin-bottom: 1rem !important;
    box-shadow: 0 2px 10px rgba(0,0,0,0.02) !important;
    border: 1px solid #e2e8f0 !important;
    background: #ffffff !important;
}

[data-testid="chatAvatarIcon-user"] {
    background-color: #3b82f6 !important;
}
[data-testid="chatAvatarIcon-assistant"] {
    background-color: #8b5cf6 !important;
}

/* Make chat input massive and floating */
[data-testid="stChatInput"] {
    background: #ffffff !important;
    border: 2px solid #bfdbfe !important;
    border-radius: 30px !important;
    box-shadow: 0 10px 30px rgba(37, 99, 235, 0.1) !important;
    padding: 5px 10px !important;
    transition: all 0.2s ease;
}
[data-testid="stChatInput"]:focus-within {
    border-color: #3b82f6 !important;
    box-shadow: 0 10px 40px rgba(37, 99, 235, 0.2) !important;
}
</style>

<div class="premium-header">
    <div class="header-badge">AI KNOWLEDGE GRAPH</div>
    <div class="header-title">Knowledge Graph Bot</div>
    <div class="header-desc">
        Interact with the intelligent knowledge base. Teach the bot new facts automatically or ask complex relational questions.
    </div>
</div>
""", unsafe_allow_html=True)

# ── Helper: Get Graphiti Flask API URL ──────────────────────────────────────
def get_graphiti_api_url() -> str:
    default = os.environ.get("GRAPHITI_API_URL", "http://localhost:8080")
    return st.session_state.get("graphiti_api_url", default)

def graphiti_post(path: str, payload: dict) -> dict:
    try:
        r = requests.post(
            f"{get_graphiti_api_url()}{path}",
            json=payload,
            timeout=30,
        )
        return r.json() if r.ok else {"error": f"HTTP {r.status_code}: {r.text}"}
    except Exception as e:
        return {"error": str(e)}

# ── Initialize chat history in session state ─────────────────────────────────

# ── Initialize chat history in session state ─────────────────────────────────
if "kg_messages" not in st.session_state:
    st.session_state.kg_messages = [
        {
            "role": "assistant",
            "content": "**Hello! I'm your AI Knowledge Assistant.**\n\nTo store facts, say `remember that Alice is a Lead Engineer`. To query, ask `What project is Alice on?`.",
            "intent": None,
        }
    ]

# ── Clear Chat Button ─────────────────────────────────────────────────────────
col1, col2 = st.columns([8, 1])
with col2:
    if st.button("Clear Chat", use_container_width=True):
        st.session_state.kg_messages = st.session_state.kg_messages[:1]
        st.rerun()

# ── Render chat history ───────────────────────────────────────────────────────
# We put the chat in a visually bounded container so it feels unified.
chat_container = st.container()

with chat_container:
    for msg in st.session_state.kg_messages:
        with st.chat_message(msg["role"]):
            if msg.get("intent") == "ingest":
                st.markdown(
                    "<span style='background:#dcfce7;color:#166534;padding:3px 12px;"
                    "border-radius:12px;font-size:0.75rem;font-weight:700;'>INGESTED</span><br><br>",
                    unsafe_allow_html=True
                )
            elif msg.get("intent") == "query":
                st.markdown(
                    "<span style='background:#dbeafe;color:#1e40af;padding:3px 12px;"
                    "border-radius:12px;font-size:0.75rem;font-weight:700;'>QUERY RESULT</span><br><br>",
                    unsafe_allow_html=True
                )
            elif msg.get("intent") == "error":
                st.markdown(
                    "<span style='background:#fee2e2;color:#991b1b;padding:3px 12px;"
                    "border-radius:12px;font-size:0.75rem;font-weight:700;'>ERROR</span><br><br>",
                    unsafe_allow_html=True
                )

            st.markdown(msg["content"])

            if msg.get("results"):
                for i, r in enumerate(msg["results"], 1):
                    score = f"{r['score']:.3f}" if r.get("score") is not None else "N/A"
                    with st.container(border=True):
                        st.markdown(f"**Result {i}** — Relevance: `{score}`")
                        st.write(r.get("fact", str(r)))

# ── Chat Input ────────────────────────────────────────────────────────────────
# Using st.chat_input which sticks to the bottom natively, but styled via CSS above.
user_input = st.chat_input("Ask a question or say 'remember that...' to store a fact...")

if user_input:
    st.session_state.kg_messages.append({
        "role": "user",
        "content": user_input,
        "intent": None,
    })

    with st.spinner("Thinking..."):
        response = graphiti_post("/api/chat", {"message": user_input})

    if "error" in response:
        assistant_msg = {
            "role": "assistant",
            "content": f"**Error:** {response['error']}\n\n"
                       f"Please check your backend configuration.",
            "intent": "error",
            "results": None,
        }
    else:
        intent = response.get("intent", "query")
        reply  = response.get("reply", "No response from the knowledge graph.")
        results = response.get("results") if intent == "query" else None

        assistant_msg = {
            "role": "assistant",
            "content": reply,
            "intent": intent,
            "results": results,
        }

    st.session_state.kg_messages.append(assistant_msg)
    st.rerun()
