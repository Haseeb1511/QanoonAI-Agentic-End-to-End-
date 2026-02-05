# Text to Speech utility for generating audio responses
from gtts import gTTS
import io


def text_to_speech(text: str, file_path: str = None) -> str:
    """
    Convert text to speech and save to file.
    
    Args:
        text: The text to convert to speech
        file_path: Optional path to save the audio file
        
    Returns:
        The file path where audio was saved
    """
    audio_obj = gTTS(text=text, lang='en')
    if file_path:
        audio_obj.save(file_path)
        return file_path
    return None


def text_to_speech_bytes(text: str) -> bytes:
    """
    Convert text to speech and return as bytes.
    Useful for streaming audio back to client.
    
    Args:
        text: The text to convert to speech
        
    Returns:
        Audio data as bytes (MP3 format)
    """
    audio_obj = gTTS(text=text, lang='en')
    audio_buffer = io.BytesIO()
    audio_obj.write_to_fp(audio_buffer)
    audio_buffer.seek(0)
    return audio_buffer.read()