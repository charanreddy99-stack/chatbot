import streamlit as st
from groq import Groq

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Mental Health AI Chatbot",
    layout="wide"
)

# --- SAFE TEXT FUNCTION ---
def clean_text(text):
    if isinstance(text, str):
        return text.encode("utf-8", "ignore").decode("utf-8")
    return text

# --- CUSTOM UI ---
st.markdown("""
<style>
body { background-color: #0e1117; }

.user-msg {
    background-color: #2563eb;
    padding: 10px;
    border-radius: 10px;
    color: white;
    margin-bottom: 8px;
    max-width: 75%;
}
.bot-msg {
    background-color: #1f2937;
    padding: 10px;
    border-radius: 10px;
    color: #e5e7eb;
    margin-bottom: 8px;
    max-width: 75%;
}

.user-container { display: flex; justify-content: flex-end; }
.bot-container { display: flex; justify-content: flex-start; }

section[data-testid="stSidebar"] {
    background-color: #dbeafe;
}

.title { text-align: center; color: #facc15; }
.subtitle { text-align: center; color: gray; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
if "all_chats" not in st.session_state:
    st.session_state.all_chats = []

if "messages" not in st.session_state:
    st.session_state.messages = []

if "api_key" not in st.session_state:
    st.session_state.api_key = None

# --- SIDEBAR ---
with st.sidebar:
    st.title("⚙️ Settings")

    api_input = st.text_input("Enter Groq API Key", type="password")
    if api_input:
        st.session_state.api_key = api_input
        st.success("API Key stored ✅")

    st.markdown("---")

    if st.button("➕ New Chat"):
        if st.session_state.messages:
            st.session_state.all_chats.append(st.session_state.messages.copy())
        st.session_state.messages = []
        st.rerun()

    if st.button("🗑 Clear Chat"):
        st.session_state.messages = []
        st.rerun()

    st.markdown("### 🕘 Previous Chats")

    for i, chat in enumerate(st.session_state.all_chats):
        if st.button(f"Chat {i+1}", key=f"chat_{i}"):
            st.session_state.messages = chat
            st.rerun()

    st.markdown("---")
    st.write("Model: openai/gpt-oss-120b")

# --- HEADER ---
st.markdown("<h1 class='title'>💬 Mental Health AI Chatbot</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Charan Reddy and Team</p>", unsafe_allow_html=True)

# --- API CHECK ---
if not st.session_state.api_key:
    st.warning("⚠️ Enter your API key in sidebar")
    st.stop()

# --- CLIENT ---
client = Groq(api_key=st.session_state.api_key)

# --- DISPLAY CHAT ---
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"""
        <div class='user-container'>
            <div class='user-msg'>🧑 {msg['content']}</div>
        </div>
        """, unsafe_allow_html=True)

    elif msg["role"] == "assistant":
        st.markdown(f"""
        <div class='bot-container'>
            <div class='bot-msg'>🤖 {msg['content']}</div>
        </div>
        """, unsafe_allow_html=True)

# --- INPUT ---
prompt = st.chat_input("Talk to me... I'm here to help 💙")

# --- HANDLE INPUT ---
if prompt:

    # Add system message once
    if len(st.session_state.messages) == 0:
        st.session_state.messages.append({
            "role": "system",
            "content": (
                "You are a compassionate mental health AI assistant. "
                "Provide emotional support and avoid medical advice."
            )
        })

    # Clean input
    prompt = clean_text(prompt)

    # Store user message
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    # Show user instantly
    st.markdown(f"""
    <div class='user-container'>
        <div class='user-msg'>🧑 {prompt}</div>
    </div>
    """, unsafe_allow_html=True)

    # API CALL (ONLY ONCE)
    with st.spinner("Thinking... 🧠"):
        try:
            safe_messages = [
                {
                    "role": m["role"],
                    "content": clean_text(m["content"])
                }
                for m in st.session_state.messages
            ]

            response = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=safe_messages
            )

            reply = clean_text(response.choices[0].message.content)

        except Exception as e:
            reply = f"❌ Error: {str(e)}"

    # Store reply
    st.session_state.messages.append({
        "role": "assistant",
        "content": reply
    })

    # Show reply
    st.markdown(f"""
    <div class='bot-container'>
        <div class='bot-msg'>🤖 {reply}</div>
    </div>
    """, unsafe_allow_html=True)
