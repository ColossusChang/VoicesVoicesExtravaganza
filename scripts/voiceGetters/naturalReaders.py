from dotenv import load_dotenv
import os
import requests
import ffmpeg
from utils.logging_config import logger
from utils.utilities import CHUNK_SIZE, WAV_DIR

load_dotenv()
headers = {
    "Accept": "audio/mpeg",
    "Content-Type": "application/json",
    "Authorization": os.getenv("NATURALREADERS_AUTH"),
    "Referer": "https://www.naturalreaders.com/",
    "Origin": "https://www.naturalreaders.com",
    "Sec-Ch-Ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": "Windows",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
}


def getSoundForLine(words: str, number: str, voice):
    display_name = voice["voice"]
    locale = voice["locale"]
    # voice_id is only present if the voice is cloned
    if voice["voice_id"] is not None:
        url = f"https://l6m5prrx81.execute-api.us-east-1.amazonaws.com/prod220818/el/speak?display_name={display_name}&speed=180&style=&locale={locale}&model=v2&voice_id={voice['voice_id']}"
    else:
        url = f"https://l6m5prrx81.execute-api.us-east-1.amazonaws.com/prod220818/el/speak?display_name={display_name}&speed=180&style=&locale={locale}&model=v2"

    payload = {"textArray": [words]}

    response = requests.request("POST", url, json=payload, headers=headers)

    # Check response status code
    if response.status_code != 200:
        logger.error(f"{response.text}")
        return

    # no extension for now
    filePath = f"{WAV_DIR}/{number}"

    with open(f"{filePath}.mp3", "wb") as f:
        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
            if chunk:
                f.write(chunk)

    # Using ffmpeg-python to convert MP3 to WAV
    ffmpeg.input(f"{filePath}.mp3", ac="1").output(
        f"{filePath}.wav", loglevel="quiet"
    ).run()

    os.remove(f"{filePath}.mp3")
