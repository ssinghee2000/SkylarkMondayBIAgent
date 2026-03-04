import streamlit as st
from llm_agent import ask_llm
from agent_controller import run_agent

st.set_page_config(page_title="Monday BI Agent", layout="wide")
st.title("Skylark BI Agent")
# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize action log
if "actions" not in st.session_state:
    st.session_state.actions = []

# Layout
chat_col, action_col = st.columns([3,1])

# Chat container (important)
with chat_col:

    chat_container = st.container()

    # Input FIRST
    user_input = st.chat_input("Ask a business question...")
    if not user_input:
        st.stop()
    if user_input:

        st.session_state.actions.clear()
        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })
        response = run_agent(user_input, st.session_state.actions)

        st.session_state.messages.append({
            "role": "assistant",
            "content": response
        })

    # Render chat history
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

# Action panel
with action_col:

    st.subheader("Agent Actions")

    if st.session_state.actions:
        for action in (st.session_state.actions):
            st.write(f"• {action}")