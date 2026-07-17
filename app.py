import os
import streamlit as st

from langchain.messages import HumanMessage

from agent import (
    agent,
    chat_with_image,
)

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
# Sidebar
# ----------------------------------------

with st.sidebar:

    st.header("Settings")

    thread_id = st.text_input(
        "Conversation ID",
        value="user_1"
    )

    uploaded_image = st.file_uploader(
        "Upload Ingredient Image",
        type=["png", "jpg", "jpeg"]
    )

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

for msg in st.session_state.messages:

    with st.chat_message(msg["role"]):

        st.markdown(msg["content"])

# ----------------------------------------
# User Prompt
# ----------------------------------------

prompt = st.chat_input(
    "Tell me your ingredients..."
)

# ----------------------------------------
# Process Request
# ----------------------------------------

if prompt:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt,
        }
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner("Cooking... 🍳"):

        # -----------------------------
        # IMAGE MODE
        # -----------------------------

        if uploaded_image is not None:

            image_path = os.path.join(
                "uploads",
                uploaded_image.name
            )

            with open(image_path, "wb") as f:
                f.write(uploaded_image.getbuffer())

            answer = chat_with_image(
                image_path=image_path,
                user_prompt=prompt,
                thread_id=thread_id,
            )

        # -----------------------------
        # TEXT MODE
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