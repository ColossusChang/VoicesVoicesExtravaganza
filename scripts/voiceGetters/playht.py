from dotenv import load_dotenv
import os
import requests
import json
import sseclient
from utils.logging_config import logger
from utils.utilities import downloadWavFile, WAV_DIR

load_dotenv()
headers = {
    "accept": "text/event-stream",
    "Authorization": os.getenv("PLAYHT_AUTH"),
    "Content-Type": "application/json",
    "X-USER-ID": os.getenv("PLAYHT_USERID"),
}


def getSoundForLine(words: str, number: str, voice):
    voiceId = voice["voice"]

    url = "https://api.play.ht/api/v2/tts"

    payload = {
        "text": words,
        "voice": voiceId,
        "output_format": "wav",
        "voice_engine": "PlayHT2.0",
        "sample_rate": 22000,
        "quality": "premium",
        # "speed": 1,
        # "seed": 411,
        # "emotion": "male_angry",  # male/female_happy/angry/sad/fearful/disgust/surprised
        # "voice_guidance": 3,
        # "style_guidance": 20,  # 1-30, how strong your chosen emotion will be.
    }

    response = requests.request("POST", url, json=payload, headers=headers)

    # log response headers
    logger.info(f"Response headers: {response.headers}")

    # Check response status code
    if response.status_code != 200:
        logger.error(f"{response.text}")
        return

    client = sseclient.SSEClient(response)

    for event in client.events():
        if event.event == "generating":
            data = json.loads(event.data)
            progress = data.get("progress")
            stage = data.get("stage")
            logger.info(f"Progress: {progress}, Stage: {stage}")
        elif event.event == "completed":
            data = json.loads(event.data)
            file_url = data.get("url")
            downloadWavFile(file_url, f"{WAV_DIR}/{number}.wav")
            break
        else:
            logger.debug(f"Unknown event: {event.event} with data: {event.data}")
