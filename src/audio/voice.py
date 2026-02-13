from openai import AsyncOpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize AsyncOpenAI client
client = AsyncOpenAI() # Automatically uses OPENAI_API_KEY from env

async def text_to_speech_bytes(text: str) -> bytes:
    """
    Convert text to speech using OpenAI TTS and return as bytes.
    Useful for streaming audio back to client.
    
    Args:
        text: The text to convert to speech
        
    Returns:
        Audio data as bytes (MP3 format)
    """
    if not text:
        raise ValueError("Text cannot be empty")
        
    try:
        response = await client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=text
        )
        # response.content is raw bytes for binary response
        return response.content
    except Exception as e:
        print(f"OpenAI TTS Error: {e}")
        raise e


# tts-1
# 1,000,000 characters → $15
# $0.06 per 4096 characters of speech