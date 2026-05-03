import streamlit as st
from groq import Groq

# --- Page Config ---
st.set_page_config(page_title="AI Chatbot", layout="wide")

# --- Session State Init ---
if "all_chats" not in st.session_state:
    st.session_state.all_chats = []

if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_index" not in st.session_state:
    st.session_state.chat_index = None

if "api_key" not in st.session_state:
    st.session_state.api_key = None

# --- Sidebar ---
with st.sidebar:
    st.title("⚙️ Settings")

    # 🔐 API Key Input
    api_input = st.text_input("Enter your Groq API Key", type="password")

    if api_input:
        st.session_state.api_key = api_input
        st.success("API Key stored in session ✅")

    st.markdown("---")

    # ➕ New Chat
    if st.button("➕ New Chat"):
        if st.session_state.messages:
            st.session_state.all_chats.append(st.session_state.messages)

        st.session_state.messages = []
        st.session_state.chat_index = None
        st.rerun()

    st.markdown("### 🕘 Previous Chats")

    # Chat history
    for i, chat in enumerate(st.session_state.all_chats):
        if st.button(f"Chat {i+1}", key=f"chat_{i}"):
            st.session_state.messages = chat
            st.session_state.chat_index = i
            st.rerun()

    st.markdown("---")
    st.write("Model: openai/gpt-oss-120b")

# --- Title ---
st.markdown(
    """
    <h1 style='text-align: center;'>💬 Mental Health AI Chatbot</h1>
    <p style='text-align: center; color: gray;'>Built by Charan Reddy</p>
    """,
    unsafe_allow_html=True
)

# --- Check API Key ---
if not st.session_state.api_key:
    st.warning("⚠️ Please enter your API key in the sidebar to start chatting.")
    st.stop()

# --- Initialize Client ---
client = Groq(api_key=st.session_state.api_key)

# --- Display Messages ---
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# --- Chat Input ---
if prompt := st.chat_input("Talk to me... I'm here to help 💙"):

    # Add system prompt once
    if len(st.session_state.messages) == 0:
        st.session_state.messages.append({
            "role": "system",
            "content": (
                "You are a compassionate mental health AI assistant. "
                "Provide emotional support, listen carefully, and respond kindly. "
                "Avoid giving medical or harmful advice."
            )
        })

    # User message
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    # --- API Call ---
    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=st.session_state.messages
        )

        reply = response.choices[0].message.content

    except Exception as e:
        reply = f"❌ Error: {str(e)}"

    # Store response
    st.session_state.messages.append({
        "role": "assistant",
        "content": reply
    })

    with st.chat_message("assistant"):
        st.markdown(reply)
