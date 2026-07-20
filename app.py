import os
import uuid
import streamlit as st

from langchain.messages import HumanMessage

from agent import (
    agent,
    chat_with_image,
)
from audio_handler import transcribe_audio

# ----------------------------------------
# Streamlit Config
# ----------------------------------------

st.set_page_config(
    page_title="🍳 Personal Chef",
    page_icon="🍳",
    layout="wide",
)

st.title("🍳 Personal Chef AI")

# ----------------------------------------
# Create uploads folder
# ----------------------------------------

os.makedirs("uploads", exist_ok=True)

# ----------------------------------------
# Conversation ID (auto-generated, not shown to the user)
# ----------------------------------------

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

thread_id = st.session_state.thread_id

# ----------------------------------------
# Sidebar
# ----------------------------------------

with st.sidebar:

    st.header("Settings")

    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# ----------------------------------------
# Memory Config
# ----------------------------------------

config = {
    "configurable": {
        "thread_id": thread_id
    }
}

# ----------------------------------------
# Chat History
# ----------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if not st.session_state.messages:
    st.markdown(
        "<h2 style='text-align: center; margin-top: 100px;'>👋 Hello! What ingredients do you have today?</h2>",
        unsafe_allow_html=True,
    )

for msg in st.session_state.messages:

    with st.chat_message(msg["role"]):

        st.markdown(msg["content"])

        # Show the thumbnail if that past message had an image attached
        if msg.get("image_path") and os.path.exists(msg["image_path"]):
            st.image(msg["image_path"], width=200)

# ----------------------------------------
# User Prompt — text, an optional attached image, and/or a mic
# recording, all live inside the same chat box.
# ----------------------------------------

chat_data = st.chat_input(
    "Tell me your ingredients...",
    accept_file=True,
    file_type=["png", "jpg", "jpeg"],
    accept_audio=True,
)

# ----------------------------------------
# Process Request
# ----------------------------------------

if chat_data:

    prompt = chat_data.text or ""
    uploaded_image = chat_data.files[0] if chat_data.files else None
    recorded_audio = chat_data.audio

    image_path = None
    transcript = None

    if uploaded_image is not None:
        image_path = os.path.join("uploads", uploaded_image.name)
        with open(image_path, "wb") as f:
            f.write(uploaded_image.getbuffer())

    if recorded_audio is not None:
        audio_path = os.path.join("uploads", "voice_input.wav")
        with open(audio_path, "wb") as f:
            f.write(recorded_audio.getbuffer())

        with st.spinner("Transcribing... 🎙️"):
            transcript = transcribe_audio(audio_path)

        # Merge spoken words with anything typed
        prompt = f"{prompt} {transcript}".strip() if prompt else transcript

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt if prompt else "(sent an image)",
            "image_path": image_path,
        }
    )

    with st.chat_message("user"):
        if prompt:
            st.markdown(prompt)
        if image_path:
            st.image(image_path, width=200)

    with st.spinner("Cooking... 🍳"):

        # -----------------------------
        # IMAGE MODE
        # -----------------------------

        if image_path is not None:

            answer = chat_with_image(
                image_path=image_path,
                user_prompt=prompt,
                thread_id=thread_id,
            )

        # -----------------------------
        # TEXT / VOICE MODE
        # -----------------------------

        else:

            response = agent.invoke(
                {
                    "messages": [
                        HumanMessage(content=prompt)
                    ]
                },
                config=config,
            )

            answer = response["messages"][-1].content

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
        }
    )

    with st.chat_message("assistant"):
        st.markdown(answer)
