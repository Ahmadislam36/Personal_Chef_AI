"""
audio_handler.py

Transcribes recorded audio to text using Groq's Whisper API.
"""

import os
from groq import Groq

if not os.getenv("GROQ_API_KEY"):
    raise ValueError(
        "Missing GROQ_API_KEY. Get a free key at https://console.groq.com/keys "
        "and add it to your .env."
    )

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# "whisper-large-v3-turbo" is faster/cheaper; "whisper-large-v3" is more accurate.
WHISPER_MODEL = "whisper-large-v3-turbo"


def transcribe_audio(audio_path: str) -> str:
    """
    Sends a recorded audio file to Groq Whisper and returns the
    transcribed text.
    """

    with open(audio_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model=WHISPER_MODEL,
            file=audio_file,
        )

    return transcript.text
