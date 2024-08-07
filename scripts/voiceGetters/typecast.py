from dotenv import load_dotenv
import os
import requests
import time
from utils.logging_config import logger
from utils.utilities import downloadWavFile, WAV_DIR

load_dotenv()
headers = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en,zh-CN;q=0.9,zh;q=0.8,ru;q=0.7,zh-TW;q=0.6,pt;q=0.5",
    "Authorization": f"Bearer {os.getenv('TYPECAST_AUTH')}",
    "Content-Type": "application/json",
    "Origin": "https://typecast.ai",
    "Priority": "u=1, i",
    "Referer": "https://typecast.ai/voice-cloning",
    "Sec-Ch-Ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
}


def getSoundForLine(words: str, number: str, voice, speed):
    voiceId = voice["voice"]
    if speed != None:
        logger.warning(
            f"Speed is not supported for Typecast. Ignoring speed value {speed}"
        )

    url = f"https://typecast.ai/api/voice-cloning/{voiceId}/speak"

    payload = [{"text": words}]

    response = requests.request("POST", url, json=payload, headers=headers)

    # Check response status code
    if response.status_code != 200:
        logger.error(f"{response.text}")
        raise Exception(f"Failed to get sound for line {number}")

    response_data = response.json()
    url1 = response_data["result"]["voice_cloning_speak_urls"][0]

    # Polling for the status
    status = "progress"
    while status == "progress":
        time.sleep(1)  # Wait for 1 second before polling again
        poll_response = requests.post(
            "https://typecast.ai/api/voice-cloning/speak/get",
            json=[url1],
            headers=headers,
        )
        poll_data = poll_response.json()
        status = poll_data["result"][0]["status"]
        if status == "done":
            url2 = poll_data["result"][0]["audio"]["url"]
            extension = poll_data["result"][0]["audio"]["extension"]

    # Download the final audio file
    audio_response = requests.get(url2, headers=headers)
    audio_url = audio_response.json()["result"]
    # Assuming wav
    downloadWavFile(audio_url, f"{WAV_DIR}/{number}.{extension}")
