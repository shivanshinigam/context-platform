import streamlit as st
import requests
import os
from datetime import datetime
from utils.api import render_sidebar_api_config

st.set_page_config(
    page_title="Knowledge OS",
    layout="centered",
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
header { visibility: hidden !important; }
footer { display: none !important; }
.stDeployButton { display: none !important; }

/* Refine chat input */
[data-testid="stChatInput"] {
    padding-bottom: 24px;
}

/* Beautiful Fade-In Animation for Cards */
@keyframes fadeUp {
    0% { opacity: 0; transform: translateY(15px); }
    100% { opacity: 1; transform: translateY(0); }
}

[data-testid="stVerticalBlockBorderWrapper"] {
    animation: fadeUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    transition: all 0.2s ease-out;
}

/* Hover effects for the native Streamlit containers */
[data-testid="stVerticalBlockBorderWrapper"]:hover {
    transform: translateY(-2px);
    border-color: #4b5563 !important;
    box-shadow: 0 8px 24px rgba(0,0,0,0.4);
}
</style>
""", unsafe_allow_html=True)

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

st.markdown(f"<h1 style='text-align: center; font-weight: 500; letter-spacing: -0.02em;'>{greeting}</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; color: #9ca3af; font-weight: 300; font-size: 1.05rem; margin-bottom: 40px;'><i>\"{st.session_state.daily_quote}\"</i></p>", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    with st.container(border=True):
        st.markdown("### 🎨 Store Knowledge")
        st.write("Teach the bot facts directly so it remembers them forever.")
        st.caption("*Example: 'Remember that Acme Corp is a premium client.'*")

with col2:
    with st.container(border=True):
        st.markdown("### 🔍 Query Graph")
        st.write("Ask complex relational questions about your ingested data.")
        st.caption("*Example: 'What projects is Alice working on?'*")
        
st.write("<br>", unsafe_allow_html=True)

with st.container(border=True):
    st.markdown("### 📁 Start from a file")
    st.write("Upload client CSVs and documents to automatically enrich the graph.")
    st.page_link("pages/2_Data_Upload.py", label="Go to Data Upload →", icon="🚀")

st.write("<br><br>", unsafe_allow_html=True)

for msg in st.session_state.kg_messages:
    # Use clean custom avatars instead of standard Streamlit heads
    avatar = "🧑‍💻" if msg["role"] == "user" else "✨"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])
        
        if msg.get("results"):
            for r in msg["results"][:3]:
                fact = r.get("fact", str(r))
                score = f"{r['score']:.2f}" if r.get("score") is not None else "High"
                st.caption(f"✓ {fact} *(Confidence: {score})*")

if user_input := st.chat_input("What do you need today? Type @ to add a file or person."):
    st.session_state.kg_messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(user_input)
        
    with st.chat_message("assistant", avatar="✨"):
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
                    st.caption(f"✓ {fact} *(Confidence: {score})*")
                    
            st.session_state.kg_messages.append({
                "role": "assistant",
                "content": reply,
                "results": results
            })
