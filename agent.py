"""
agent.py

Creates the Personal Chef Agent using LangChain + LangGraph.
"""

import os
from dotenv import load_dotenv

from langchain_openai import AzureChatOpenAI
from langchain.agents import create_agent
from langchain.messages import HumanMessage

from prompts import SYSTEM_PROMPT
from memory import memory, get_config

from tools import (
    web_search,
    validate_ingredients,
    validate_cuisine,
    nutrition_estimator,
)

from image_handler import identify_ingredients

# ---------------------------------------------------------
# Load Environment Variables
# ---------------------------------------------------------

load_dotenv()

REQUIRED_AZURE_VARS = [
    "AZURE_OPENAI_ENDPOINT",
    "AZURE_OPENAI_API_KEY",
    "OPENAI_API_VERSION",
    "AZURE_CHAT_MODEL_DEPLOYMENT",
]

missing = [var for var in REQUIRED_AZURE_VARS if not os.getenv(var)]

if missing:
    raise ValueError(f"Missing required Azure OpenAI env vars: {', '.join(missing)}")

# ---------------------------------------------------------
# Initialize Azure OpenAI Model (gpt-4o)
# ---------------------------------------------------------

model = AzureChatOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("OPENAI_API_VERSION"),
    azure_deployment=os.getenv("AZURE_CHAT_MODEL_DEPLOYMENT"),
    temperature=0.3,
)

# ---------------------------------------------------------
# Register Tools
# ---------------------------------------------------------

tools = [
    web_search,
    validate_ingredients,
    validate_cuisine,
    nutrition_estimator,
]

# ---------------------------------------------------------
# Create Agent
# ---------------------------------------------------------

agent = create_agent(
    model=model,
    tools=tools,
    system_prompt=SYSTEM_PROMPT,
    checkpointer=memory,
)

# =========================================================
# TEXT CHAT
# =========================================================

def chat(
    message: str,
    thread_id: str = "default",
):
    """
    Normal text conversation.
    """

    config = get_config(thread_id)

    question = HumanMessage(
        content=message
    )

    response = agent.invoke(
        {
            "messages": [question]
        },
        config=config,
    )

    return response["messages"][-1].content


# =========================================================
# IMAGE CHAT
# =========================================================

def chat_with_image(
    image_path: str,
    user_prompt: str = "",
    thread_id: str = "default",
):
    """
    User uploads image.
    Azure gpt-4o detects ingredients and generates the recipe.
    """

    ingredients = identify_ingredients(image_path)

    prompt = f"""
The user uploaded a food image.

Detected ingredients:

{ingredients}

User Request:

{user_prompt}

Use ONLY Pakistani,
Indian,
Chinese,
or Italian cuisine.

If web search is useful,
use it before answering.

Provide recipes.
"""

    config = get_config(thread_id)

    question = HumanMessage(
        content=prompt
    )

    response = agent.invoke(
        {
            "messages": [question]
        },
        config=config,
    )

    return response["messages"][-1].content


# =========================================================
# AUDIO CHAT
# =========================================================

def chat_with_audio(
    transcript: str,
    thread_id: str = "default",
):
    """
    Audio transcription already completed.

    Agent receives transcript.
    """

    config = get_config(thread_id)

    question = HumanMessage(
        content=transcript
    )

    response = agent.invoke(
        {
            "messages": [question]
        },
        config=config,
    )

    return response["messages"][-1].content


# =========================================================
# MULTIMODAL CHAT
# =========================================================

def multimodal_chat(
    image_path: str,
    transcript: str,
    thread_id: str = "default",
):
    """
    Image + Audio together.
    """

    ingredients = identify_ingredients(image_path)

    prompt = f"""
Detected ingredients:

{ingredients}

User said:

{transcript}

Use web search if needed.

Recommend recipes.

Only recommend

Pakistani

Indian

Chinese

Italian

food.
"""

    config = get_config(thread_id)

    response = agent.invoke(
        {
            "messages": [
                HumanMessage(content=prompt)
            ]
        },
        config=config,
    )

    return response["messages"][-1].content


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    print("=" * 60)
    print("🍳 Personal Chef")
    print("=" * 60)

    while True:

        question = input("\nYou : ")

        if question.lower() == "exit":
            break

        answer = chat(question)

        print("\nChef:\n")
        print(answer)