import json
import requests
from utils.logging_config import logger

CHUNK_SIZE = 1024
WAV_DIR = "../bg/vveBG/WAV"


def loadDictFromJson(file_path):
    # Open the JSON file
    with open(file_path, "r") as file:
        # Load the JSON data
        data = json.load(file)

    # Return the loaded dictionary
    return data


voiceIds = loadDictFromJson("static/voices.json")


def getVoice(creatureId: str):
    if creatureId not in voiceIds:
        raise ValueError(f"Creature with ID {creatureId} not found")
    return voiceIds[creatureId]


def downloadWavFile(url: str, path: str):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(path, "wb") as f:
            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                if chunk:
                    f.write(chunk)
        logger.info(f"Downloaded WAV file to {path}")
    else:
        logger.error(f"Failed to download WAV file: {response.status_code}")
