from pydub import AudioSegment
from openai import AsyncOpenAI
from dotenv import load_dotenv  
from fastapi.concurrency import run_in_threadpool
import asyncio

load_dotenv()

client = AsyncOpenAI()

class AudioToText:
    async def transcribe(self, audio_path: str) -> str:
        try:
            # Convert webm to wav if needed (CPU bound, run in threadpool)
            if audio_path.endswith(".webm"):
                wav_path = audio_path.replace(".webm", ".wav")
                
                def convert():
                    AudioSegment.from_file(audio_path, format="webm").export(wav_path, format="wav")
                
                await run_in_threadpool(convert)
                audio_path = wav_path

            # Open file and send to OpenAI (I/O bound)
            with open(audio_path, "rb") as audio:
                transcript = await client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio,
                language="en",
                temperature=0,
                prompt="Transcribe the following audio in English."
            ) #type:ignore
            return transcript.text
        except Exception as e:
            print("Transcription error:", e)
            return "[Transcription failed]"
