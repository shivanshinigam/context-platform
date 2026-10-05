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

# ── HIDE HEADER & FOOTER ──────────────────────────────────────────────────────
css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

header { visibility: hidden !important; }
footer { display: none !important; }
.stDeployButton { display: none !important; }

/* Apply Inter font */
html, body, [class*="css"], [class*="st-"] {
    font-family: 'Inter', sans-serif !important;
}

/* Empty State Styling */
.empty-wrapper {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding-top: 10vh;
}
.greeting {
    font-size: 2.2rem;
    font-weight: 600;
    margin-bottom: 12px;
    letter-spacing: -0.02em;
}
.sub-greeting {
    font-size: 1.05rem;
    color: #9ca3af;
    margin-bottom: 48px;
    text-align: center;
    max-width: 650px;
    line-height: 1.5;
}
.cards-row {
    display: flex;
    gap: 20px;
    justify-content: center;
    flex-wrap: wrap;
    max-width: 900px;
}
.card {
    background: #222222;
    border: 1px solid #333333;
    border-radius: 16px;
    padding: 28px 24px;
    flex: 1;
    min-width: 250px;
    transition: all 0.2s ease;
}
.card:hover {
    background: #2a2a2a;
    border-color: #444444;
}
.card-icon {
    font-size: 1.8rem;
    margin-bottom: 16px;
}
.card-title {
    font-weight: 600;
    font-size: 1.1rem;
    margin-bottom: 10px;
    color: #ffffff;
}
.card-text {
    font-size: 0.9rem;
    color: #9ca3af;
    line-height: 1.5;
}
.card-text b {
    color: #d1d5db;
}
</style>
"""
# Rendered without indentation to avoid markdown code block bugs
st.markdown(css, unsafe_allow_html=True)

# ── EMPTY STATE ───────────────────────────────────────────────────────────────
if not st.session_state.kg_messages:
    hour = datetime.now().hour
    greeting = "Good Morning" if hour < 12 else ("Good Afternoon" if hour < 17 else "Good Evening")
    
    empty_html = f"""
<div class="empty-wrapper">
<div class="greeting">{greeting}, Shivanshi</div>
<div class="sub-greeting">
This AI Assistant connects directly to your Graphiti Knowledge Base. It continuously learns from the documents you upload and the facts you teach it.
</div>

<div class="cards-row">
<div class="card">
<div class="card-icon">🧠</div>
<div class="card-title">Store Knowledge</div>
<div class="card-text">Teach the bot facts directly.<br/><br/><i>Example: "Remember that Alice is managing the AWS migration."</i></div>
</div>
<div class="card">
<div class="card-icon">🔍</div>
<div class="card-title">Query Graph</div>
<div class="card-text">Ask complex relational questions.<br/><br/><i>Example: "What project is Alice working on?"</i></div>
</div>
<div class="card">
<div class="card-icon">📁</div>
<div class="card-title">Client Uploads</div>
<div class="card-text">Use the <b>Data Upload</b> tab to ingest CSVs and documents. The bot will automatically learn from them.</div>
</div>
</div>
</div>
"""
    st.markdown(empty_html, unsafe_allow_html=True)

# ── CHAT HISTORY (NATIVE) ─────────────────────────────────────────────────────
for msg in st.session_state.kg_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        
        if msg.get("results"):
            for r in msg["results"][:3]:
                fact = r.get("fact", str(r))
                score = f"{r['score']:.2f}" if r.get("score") is not None else "High"
                st.caption(f"✓ **{fact}** *(Confidence: {score})*")

# ── NATIVE INPUT ──────────────────────────────────────────────────────────────
if user_input := st.chat_input("What do you need today? Type @ to add a file or person."):
    st.session_state.kg_messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
        
    with st.chat_message("assistant"):
        with st.spinner("Processing..."):
            response = graphiti_post("/api/chat", {"message": user_input})
            
        if "error" in response:
            error_msg = f"Failed to connect: {response['error']}"
            st.error(error_msg)
            st.session_state.kg_messages.append({"role": "assistant", "content": error_msg})
        else:
            reply = response.get("reply", "Done.")
            results = response.get("results")
            
            st.markdown(reply)
            if results:
                for r in results[:3]:
                    fact = r.get("fact", str(r))
                    score = f"{r['score']:.2f}" if r.get("score") is not None else "High"
                    st.caption(f"✓ **{fact}** *(Confidence: {score})*")
                    
            st.session_state.kg_messages.append({
                "role": "assistant",
                "content": reply,
                "results": results
            })
