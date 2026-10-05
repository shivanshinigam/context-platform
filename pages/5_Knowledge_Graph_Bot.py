import streamlit as st
import requests
import os
from datetime import datetime

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

# ── CONTEXT.AI EXACT DARK THEME CSS ──────────────────────────────────────────
css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

/* Hide Streamlit top header */
header { visibility: hidden !important; }
footer { display: none !important; }
.stDeployButton { display: none !important; }

/* Main app background */
.stApp, .main .block-container {
    background-color: #1a1a1a !important;
    color: #ffffff !important;
    font-family: 'Inter', sans-serif !important;
}
.main .block-container {
    padding: 0 !important;
    max-width: 100% !important;
}

/* Sidebar styling (keep it visible but dark to match) */
[data-testid="stSidebar"] {
    background-color: #141414 !important;
    border-right: 1px solid #2a2a2a !important;
}
[data-testid="stSidebar"] * {
    color: #e0e0e0 !important;
}

/* ── EXACT CONTEXT.AI LAYOUT ── */
.context-wrapper {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 80vh; /* leave room for input */
    padding: 0 40px;
}

.greeting-row {
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 40px;
    width: 100%;
    max-width: 800px;
}

.greeting-icon {
    display: flex;
    align-items: flex-end;
    gap: 3px;
    height: 24px;
}
.greeting-icon span {
    display: block;
    width: 4px;
    background-color: #d1d5db;
    border-radius: 2px;
}
.greeting-icon span:nth-child(1) { height: 12px; }
.greeting-icon span:nth-child(2) { height: 20px; }
.greeting-icon span:nth-child(3) { height: 24px; }
.greeting-icon span:nth-child(4) { height: 16px; }

.greeting-text {
    font-size: 1.75rem;
    font-weight: 600;
    color: #ffffff;
    letter-spacing: -0.02em;
}

.cards-container {
    display: flex;
    gap: 16px;
    width: 100%;
    max-width: 800px;
}

.cards-left {
    display: flex;
    flex-direction: column;
    gap: 16px;
    flex: 1;
}

.card {
    background: #222222;
    border: 1px solid #333333;
    border-radius: 16px;
    padding: 24px;
    cursor: pointer;
    transition: all 0.2s ease;
    position: relative;
    overflow: hidden;
}
.card:hover {
    background: #2a2a2a;
    border-color: #444444;
}

.card-icon {
    font-size: 1.2rem;
    margin-bottom: 12px;
}

.card-title {
    font-size: 1rem;
    font-weight: 600;
    color: #ffffff;
    margin-bottom: 4px;
    display: flex;
    align-items: center;
    gap: 4px;
}
.card-sub {
    font-size: 0.85rem;
    color: #9ca3af;
}

.card.make { flex: 1; }
.card.build { flex: 1; }
.card.start {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
}

.start-icon {
    width: 48px;
    height: 48px;
    margin-bottom: 16px;
    opacity: 0.8;
}

/* ── CHAT MESSAGES ── */
.chat-area {
    padding: 40px 40px 140px;
    display: flex;
    flex-direction: column;
    gap: 24px;
    align-items: center;
    width: 100%;
}
.msg-row {
    display: flex;
    width: 100%;
    max-width: 800px;
    gap: 16px;
}
.msg-row.user { justify-content: flex-end; }
.msg-row.assistant { justify-content: flex-start; }

.bubble {
    padding: 16px 20px;
    border-radius: 12px;
    font-size: 0.95rem;
    line-height: 1.6;
    max-width: 80%;
}
.bubble.user {
    background: #2d2d2d;
    color: #ffffff;
}
.bubble.assistant {
    background: transparent;
    color: #e5e7eb;
}

.tag {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    margin-bottom: 8px;
}
.tag-stored { background: #064e3b; color: #34d399; }
.tag-query { background: #1e3a8a; color: #60a5fa; }
.tag-error { background: #7f1d1d; color: #f87171; }

.citation {
    background: #222222;
    border: 1px solid #333;
    padding: 12px;
    border-radius: 8px;
    margin-top: 8px;
    font-size: 0.85rem;
    color: #a3a3a3;
}

/* ── INPUT AREA (To match Context.ai fat bar) ── */
[data-testid="stChatInput"] {
    max-width: 800px;
    margin: 0 auto;
    padding-bottom: 32px;
}
[data-testid="stChatInput"] > div {
    background: #222222 !important;
    border: 1px solid #333333 !important;
    border-radius: 16px !important;
    padding: 12px 16px !important; /* Fat input */
}
[data-testid="stChatInput"] > div:focus-within {
    border-color: #555555 !important;
}
[data-testid="stChatInput"] textarea {
    color: #ffffff !important;
    font-size: 1rem !important;
    background: transparent !important;
}
[data-testid="stChatInput"] textarea::placeholder {
    color: #6b7280 !important;
}
[data-testid="stChatInput"] button {
    background: #333333 !important;
    color: #ffffff !important;
    border-radius: 8px !important;
}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# ── LOGIC ──
hour = datetime.now().hour
greeting = "Good Morning" if hour < 12 else ("Good Afternoon" if hour < 17 else "Good Evening")

if not st.session_state.kg_messages:
    # EXACT Context.ai Empty State
    empty_html = f"""
<div class="context-wrapper">
<div class="greeting-row">
<div class="greeting-icon">
<span></span><span></span><span></span><span></span>
</div>
<div class="greeting-text">{greeting}, Shivanshi</div>
</div>

<div class="cards-container">
<div class="cards-left">
<div class="card make">
<div class="card-icon">🎨</div>
<div class="card-title">Make &rsaquo;</div>
<div class="card-sub">Decks, docs and video from your files</div>
</div>
<div class="card build">
<div class="card-icon">🔨</div>
<div class="card-title">Build &rsaquo;</div>
<div class="card-sub">Tools and agents your team can use</div>
</div>
</div>
<div class="card start">
<svg class="start-icon" viewBox="0 0 24 24" fill="none" stroke="#6b7280" stroke-width="1.5">
<path d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"/>
</svg>
<div class="card-title" style="justify-content:center">Start from a file</div>
<div class="card-sub">Drop one here to see what it can become</div>
</div>
</div>
</div>
"""
    st.markdown(empty_html, unsafe_allow_html=True)

else:
    # Chat State
    st.markdown('<div class="chat-area">', unsafe_allow_html=True)
    for msg in st.session_state.kg_messages:
        role = msg["role"]
        content = msg["content"]
        intent = msg.get("intent")
        
        if role == "user":
            html = f"""
<div class="msg-row user">
<div class="bubble user">{content}</div>
</div>
"""
            st.markdown(html, unsafe_allow_html=True)
        else:
            tag_html = ""
            if intent == "ingest": tag_html = '<div class="tag tag-stored">Stored</div>'
            elif intent == "query": tag_html = '<div class="tag tag-query">Retrieved</div>'
            elif intent == "error": tag_html = '<div class="tag tag-error">Error</div>'
            
            citations_html = ""
            if msg.get("results"):
                for r in msg["results"][:3]:
                    fact = r.get("fact", str(r))
                    score = f"{r['score']:.2f}" if r.get("score") is not None else "High"
                    citations_html += f"""
<div class="citation">
<strong style="color:#d1d5db; font-size:0.75rem;">Conf: {score}</strong><br/>
{fact}
</div>
"""
            
            html = f"""
<div class="msg-row assistant">
<div class="bubble assistant">
{tag_html}
<div style="margin-top:4px">{content}</div>
{citations_html}
</div>
</div>
"""
            st.markdown(html, unsafe_allow_html=True)
            
    st.markdown('</div>', unsafe_allow_html=True)

# ── INPUT ──
if user_input := st.chat_input("What do you need today? Type @ to add a file or person."):
    st.session_state.kg_messages.append({"role": "user", "content": user_input, "intent": None})
    
    with st.spinner("Processing..."):
        response = graphiti_post("/api/chat", {"message": user_input})
        
    if "error" in response:
        st.session_state.kg_messages.append({"role": "assistant", "content": f"Failed: {response['error']}", "intent": "error"})
    else:
        st.session_state.kg_messages.append({
            "role": "assistant",
            "content": response.get("reply", "Done."),
            "intent": response.get("intent", "query"),
            "results": response.get("results")
        })
        
    st.rerun()
