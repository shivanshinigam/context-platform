import streamlit as st
import requests
import os

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
    st.session_state.kg_messages = [
        {"role": "assistant", "content": "Welcome to Knowledge OS. How can I assist you today?", "intent": None}
    ]

# ── PREMIUM CSS & LAYOUT ──────────────────────────────────────────────────────
css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

/* Reset Streamlit chrome */
header { visibility: hidden !important; }
footer { display: none !important; }
.stDeployButton { display: none !important; }
.main .block-container { 
    padding: 0 !important; 
    max-width: 100% !important; 
    background: #F9FAFB;
}
html, body, [class*="css"], [class*="st-"] {
    font-family: 'Inter', sans-serif !important;
}

/* Sidebar styling */
[data-testid="stSidebar"] {
    background: #FFFFFF !important;
    border-right: 1px solid #E5E7EB !important;
}

/* Custom Header */
.premium-header {
    background: rgba(255, 255, 255, 0.85);
    backdrop-filter: blur(12px);
    border-bottom: 1px solid #E5E7EB;
    padding: 16px 40px;
    display: flex;
    align-items: center;
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    z-index: 999;
}
.header-title {
    font-size: 1.1rem;
    font-weight: 600;
    color: #111827;
}
.pulse-dot {
    width: 8px;
    height: 8px;
    background: #10B981;
    border-radius: 50%;
    margin-left: 12px;
    box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.2);
}
.header-status {
    font-size: 0.8rem;
    color: #6B7280;
    margin-left: 6px;
    font-weight: 500;
}

/* Chat Layout */
.chat-wrapper {
    padding: 80px 40px 140px;
    display: flex;
    flex-direction: column;
    gap: 24px;
    align-items: center;
}

.msg-row {
    display: flex;
    width: 100%;
    max-width: 800px;
    gap: 16px;
    animation: fadeIn 0.3s ease-out;
}
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}
.msg-row.user { justify-content: flex-end; }
.msg-row.assistant { justify-content: flex-start; }

/* Avatars */
.avatar {
    width: 36px;
    height: 36px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}
.avatar.ai {
    background: linear-gradient(135deg, #3B82F6, #8B5CF6);
    color: white;
}

/* Bubbles */
.bubble {
    max-width: 80%;
    padding: 16px 20px;
    font-size: 0.95rem;
    line-height: 1.6;
}
.bubble.user {
    background: linear-gradient(135deg, #1E293B, #0F172A);
    color: #FFFFFF;
    border-radius: 20px 20px 4px 20px;
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
}
.bubble.assistant {
    background: #FFFFFF;
    color: #1F2937;
    border: 1px solid #E5E7EB;
    border-radius: 20px 20px 20px 4px;
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.03);
}

/* Tags */
.intent-tag {
    display: inline-flex;
    align-items: center;
    padding: 4px 10px;
    border-radius: 12px;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    margin-bottom: 12px;
}
.intent-tag.stored { background: #ECFDF5; color: #059669; border: 1px solid #D1FAE5; }
.intent-tag.query { background: #EFF6FF; color: #2563EB; border: 1px solid #DBEAFE; }
.intent-tag.error { background: #FEF2F2; color: #DC2626; border: 1px solid #FEE2E2; }

/* Citations */
.citation {
    background: #F9FAFB;
    border: 1px solid #F3F4F6;
    border-radius: 12px;
    padding: 12px 16px;
    margin-top: 12px;
    font-size: 0.85rem;
    color: #4B5563;
}
.citation-header {
    font-weight: 600;
    color: #374151;
    margin-bottom: 4px;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* Input Area Override */
[data-testid="stChatInput"] {
    max-width: 800px;
    margin: 0 auto;
}
[data-testid="stChatInput"] > div {
    background: #FFFFFF !important;
    border: 1px solid #E5E7EB !important;
    border-radius: 24px !important;
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05) !important;
    padding: 4px 12px !important;
}
[data-testid="stChatInput"] > div:focus-within {
    border-color: #3B82F6 !important;
    box-shadow: 0 10px 25px -5px rgba(59, 130, 246, 0.15) !important;
}
[data-testid="stChatInput"] textarea {
    font-size: 1rem !important;
}
</style>
"""
# Must be rendered without leading spaces to avoid Markdown code block formatting
st.markdown(css, unsafe_allow_html=True)

header_html = """
<div class="premium-header">
<div class="header-title">Knowledge OS</div>
<div class="pulse-dot"></div>
<div class="header-status">Live</div>
</div>
"""
st.markdown(header_html, unsafe_allow_html=True)

chat_wrapper_start = """<div class="chat-wrapper">"""
st.markdown(chat_wrapper_start, unsafe_allow_html=True)

# ── RENDER CHAT ───────────────────────────────────────────────────────────────
for msg in st.session_state.kg_messages:
    role = msg["role"]
    content = msg["content"]
    intent = msg.get("intent")
    
    if role == "user":
        # NO INDENTATION ALLOWED in HTML strings rendered by Streamlit Markdown!
        html = f"""
<div class="msg-row user">
<div class="bubble user">{content}</div>
</div>
"""
        st.markdown(html, unsafe_allow_html=True)
    else:
        tag_html = ""
        if intent == "ingest":
            tag_html = '<div class="intent-tag stored">Knowledge Stored</div>'
        elif intent == "query":
            tag_html = '<div class="intent-tag query">Knowledge Retrieved</div>'
        elif intent == "error":
            tag_html = '<div class="intent-tag error">System Error</div>'
            
        citations_html = ""
        if msg.get("results"):
            for r in msg["results"][:3]:
                fact = r.get("fact", str(r))
                score = f"{r['score']:.2f}" if r.get("score") is not None else "High"
                citations_html += f"""
<div class="citation">
<div class="citation-header">Confidence: {score}</div>
{fact}
</div>
"""

        html = f"""
<div class="msg-row assistant">
<div class="avatar ai">
<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
</div>
<div class="bubble assistant">
{tag_html}
<div class="msg-content">{content}</div>
{citations_html}
</div>
</div>
"""
        st.markdown(html, unsafe_allow_html=True)

chat_wrapper_end = """</div>"""
st.markdown(chat_wrapper_end, unsafe_allow_html=True)

# ── HANDLE INPUT ──────────────────────────────────────────────────────────────
if user_input := st.chat_input("Ask a question or teach me a fact..."):
    st.session_state.kg_messages.append({"role": "user", "content": user_input, "intent": None})
    
    with st.spinner("Processing..."):
        response = graphiti_post("/api/chat", {"message": user_input})
        
    if "error" in response:
        st.session_state.kg_messages.append({"role": "assistant", "content": f"Failed to connect: {response['error']}", "intent": "error"})
    else:
        st.session_state.kg_messages.append({
            "role": "assistant",
            "content": response.get("reply", "Done."),
            "intent": response.get("intent", "query"),
            "results": response.get("results")
        })
        
    st.rerun()
