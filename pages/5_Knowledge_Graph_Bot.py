import streamlit as st
import requests
import os

st.set_page_config(
    page_title="Knowledge Assistant",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ── Clean up Streamlit Chrome ────────────────────────────────────────────────
st.markdown("""
<style>
/* Hide deploy button and footer for a cleaner look */
.stDeployButton { display: none !important; }
footer { display: none !important; }
/* Make the top padding smaller so chat is prominent */
.main .block-container { padding-top: 3rem !important; }
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

# ── Header ────────────────────────────────────────────────────────────────────
st.title("Knowledge Assistant")
st.markdown("Ask me anything, or teach me a new fact about your team by saying *'remember that...'*")
st.divider()

# ── Session state ─────────────────────────────────────────────────────────────
if "kg_messages" not in st.session_state:
    st.session_state.kg_messages = []

# ── Render chat history ───────────────────────────────────────────────────────
for msg in st.session_state.kg_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        
        # Display knowledge graph results if they exist
        if msg.get("results"):
            for r in msg["results"][:4]:
                score = f"{r['score']:.2f}" if r.get("score") is not None else "–"
                fact = r.get("fact", str(r))
                st.caption(f"✓ **{fact}** *(Confidence: {score})*")

# ── Chat input ────────────────────────────────────────────────────────────────
if user_input := st.chat_input("Message Knowledge Assistant..."):
    # Show user message immediately
    st.session_state.kg_messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Fetch and show assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = graphiti_post("/api/chat", {"message": user_input})

        if "error" in response:
            error_msg = "Something went wrong communicating with the Graphiti backend."
            st.error(error_msg)
            st.session_state.kg_messages.append({"role": "assistant", "content": error_msg})
        else:
            reply = response.get("reply", "No response.")
            results = response.get("results")
            
            st.markdown(reply)
            
            if results:
                for r in results[:4]:
                    score = f"{r['score']:.2f}" if r.get("score") is not None else "–"
                    fact = r.get("fact", str(r))
                    st.caption(f"✓ **{fact}** *(Confidence: {score})*")
                    
            st.session_state.kg_messages.append({
                "role": "assistant",
                "content": reply,
                "results": results
            })
