"""
image_handler.py

Handles image understanding using Gemini Vision.
Extracts visible food ingredients from an uploaded image.
"""

import os
import base64
from dotenv import load_dotenv

from langchain_core.messages import HumanMessage

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

# Vision model (gpt-4o is multimodal, same deployment as chat)

from langchain_openai import AzureChatOpenAI

vision_model = AzureChatOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("OPENAI_API_VERSION"),
    azure_deployment=os.getenv("AZURE_CHAT_MODEL_DEPLOYMENT"),
    temperature=0,
)


def image_to_base64(image_path: str) -> str:
    """
    Convert image into Base64.
    """

    with open(image_path, "rb") as image:
        return base64.b64encode(image.read()).decode("utf-8")


def identify_ingredients(image_path: str) -> str:
    """
    Detect ingredients from a food image.
    """

    img_b64 = image_to_base64(image_path)

    message = HumanMessage(
        content=[
            {
                "type": "text",
                "text": """
You are an ingredient detector.

Look carefully at the image.

Return ONLY:

Detected Ingredients:
- ingredient 1
- ingredient 2
- ingredient 3

Do not explain anything.
Do not write recipes.
Do not guess hidden ingredients.
Only list ingredients that are clearly visible.
"""
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{img_b64}"
                },
            },
        ]
    )

    response = vision_model.invoke([message])

    return response.content
