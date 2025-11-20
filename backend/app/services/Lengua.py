import asyncio
import wave
from openai import AsyncOpenAI
from openai.helpers import LocalAudioPlayer
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv("backend/.env")
api_key = os.getenv("OPENAI_API_KEY")
openai = AsyncOpenAI(api_key=api_key)

AUDIO_PATH = Path(__file__).parent.parent / "audio"

async def generar_audio(input: str, id, contador = 0) -> None:

    async with openai.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice="ash",
        input=input,
        response_format="pcm",
    ) as response:
    
        with open(f"{AUDIO_PATH}/output{id}_{contador}.pcm", "wb") as f:
            async for chunk in response.iter_bytes():
                f.write(chunk)
        pcm_file = f"{AUDIO_PATH}/output{id}_{contador}.pcm"
        wav_file = f"{AUDIO_PATH}/output{id}_{contador}.wav"

        with open(pcm_file, "rb") as pcm, wave.open(wav_file, "wb") as wav:
            wav.setnchannels(1)  # Mono
            wav.setsampwidth(2)  # 16 bits por muestra
            wav.setframerate(24000)  # Frecuencia de muestreo

            wav.writeframes(pcm.read())