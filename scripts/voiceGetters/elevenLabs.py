import os
import requests
import ffmpeg
from utils.logging_config import logger
from utils.utilities import CHUNK_SIZE, WAV_DIR

MODEL = "eleven_turbo_v2"

headers = {
    "Accept": "audio/mpeg",
    "Content-Type": "application/json",
    "xi-api-key": os.getenv("ELEVENLABS_API_KEY"),
}


def getSoundForLine(words: str, number: str, voice):
    voiceId = voice["voice"]

    url = (
        f"https://api.elevenlabs.io/v1/text-to-speech/{voiceId}?output_format=pcm_22050"
    )

    payload = {
        "text": words,
        "model_id": MODEL,
        "seed": 123,
        "stability": 0.8,
        "similarity_boost": 0.7,
        # "previous_text": "<string>",
        # "next_text": "<string>",
        # "previous_request_ids": ["<string>"],
        # "next_request_ids": ["<string>"],
    }

    response = requests.request("POST", url, json=payload, headers=headers)

    # Check response status code
    if response.status_code != 200:
        logger.error(f"{response.text}")
        raise Exception(f"Failed to get sound for line {number}")

    # no extension for now
    filePath = f"{WAV_DIR}/{number}"

    with open(f"{filePath}.pcm", "wb") as f:
        # with open('output.mp3', 'wb') as f:
        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
            if chunk:
                f.write(chunk)

    # Using ffmpeg-python to convert PCM to WAV
    ffmpeg.input(f"{filePath}.pcm", format="s16le", ar="22050", ac="1").output(
        f"{filePath}.wav", loglevel="quiet"
    ).run()

    os.remove(f"{filePath}.pcm")
