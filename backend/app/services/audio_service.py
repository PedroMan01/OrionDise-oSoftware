import asyncio
from openai import AsyncOpenAI
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv(Path(__file__).parent.parent.parent / ".env")

class AudioService:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            print("Warning: OPENAI_API_KEY not found in environment variables.")
        self.client = AsyncOpenAI(api_key=self.api_key)
        self.audio_path = Path(__file__).parent.parent / "audio"
        
        # Ensure audio directory exists
        if not self.audio_path.exists():
            self.audio_path.mkdir(parents=True, exist_ok=True)

    async def generate_audio(self, text: str, user_id=0, instructions: str = None) -> str:
        """
        Generates TTS audio using gpt-4o-mini-tts and voice 'ash', using instructions if available.
        """
        try:
            wav_filename = f"output{user_id}.wav"
            wav_path = self.audio_path / wav_filename

            # Debug print
            if instructions:
                print(f"DEBUG: Generating audio with instructions: {instructions}")

            response = await self.client.audio.speech.create(
                model="gpt-4o-mini-tts", 
                voice="ash", 
                input=text,
                # instructions=instructions, # Reverting to keep consistent if user desired
                response_format="wav",
            )

            
            # Save using the async method
            await response.astream_to_file(wav_path)
            
            return wav_filename
            
        except Exception as e:
            print(f"Error generating audio: {e}")
            return None

    async def generate_audio_direct_wav(self, text: str, user_id=0) -> str:
        """
        Generates TTS audio using gpt-4o-mini-tts directly to WAV format.
        """
        wav_filename = f"output{user_id}.wav"
        wav_path = self.audio_path / wav_filename
        
        try:
            response = await self.client.audio.speech.create(
                model="gpt-4o-mini-tts",
                voice="ash",
                input=text,
                response_format="wav"
            )
            
            await response.astream_to_file(wav_path)
            return wav_filename
        except Exception as e:
            print(f"Error generating audio (WAV): {e}")
            return None

    async def transcribe_audio(self, file_path: Path) -> str:
        """
        Transcribes audio file using Whisper (whisper-1).
        """
        try:
            with open(file_path, "rb") as audio_file:
                transcription = await self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="es"
                )
            return transcription.text
        except Exception as e:
            print(f"Error transcribing audio: {e}")
            return None

# Singleton instance
audio_service = AudioService()