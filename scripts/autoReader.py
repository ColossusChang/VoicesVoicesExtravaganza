from datetime import datetime
import json
import shutil
import sys
import argparse
import os
import random
from getSound import getSoundsForCreature
from utils.logging_config import logger
from utils.utilities import loadDictFromJson, TXT_DIR, WAV_DIR
from concat import do_concatenation

VOICELAB_DIR = "../NOTES/voicelab"
ORIG_AUDIO_DIR = f"{VOICELAB_DIR}/orig_audio"

# Load global variables
voices = loadDictFromJson("static/voices.json")
companions = loadDictFromJson("static/companions.json")
creatures = loadDictFromJson("static/creatures.json")
similarContent = loadDictFromJson("static/allSimilarContent.json")
naturalReaderVoices = loadDictFromJson("static/naturalReaderVoices.json")
exempt = loadDictFromJson("static/onHold.json")


def original_audio_paths_getter(name: str) -> list:
    originalAudioPaths = []
    while True:
        i = len(originalAudioPaths) + 1
        originalAudioPath = os.path.join(ORIG_AUDIO_DIR, f"{name}{i:02d}.WAV")
        logger.info(f"Checking existence of {originalAudioPath}")
        if os.path.exists(originalAudioPath):
            originalAudioPaths.append(originalAudioPath)
        else:
            break
    return originalAudioPaths


def copy_and_concat_audio(name: str, originalAudioPaths) -> list:
    # If the directory does not already exist, create a new directory VOICELAB_DIR/name and copy the original audio files there.
    creatureDir = os.path.join(VOICELAB_DIR, name)
    if not os.path.exists(creatureDir):
        os.makedirs(creatureDir)
        for originalAudioPath in originalAudioPaths:
            shutil.copy(
                originalAudioPath,
                os.path.join(creatureDir, os.path.basename(originalAudioPath)),
            )
        # concat the audios
        do_concatenation(name)
        logger.info(
            f"Copied original audio files to directory {creatureDir}, and concatenated them to {creatureDir}/{name}.wav. "
        )
    else:
        logger.info(
            f"Directory {creatureDir} already exists. Skipping copying original audio files."
        )


def auditCreatures(limit: int):
    results = {
        "unprocessable_creatures": [],
        "creatures_with_original_audio": [],
        "new_voices": {},
    }
    for creature_id in os.listdir(TXT_DIR):
        if limit == 0:
            break

        subDirPath = os.path.join(TXT_DIR, creature_id)
        if 1 and os.path.isdir(subDirPath):
            logger.info(f"Processing creature: {creature_id}")

            if creature_id in exempt:
                logger.info(f"Skipping {creature_id} because it is on hold.")
                continue

            if creature_id in voices:
                continue

            # Try to see if the creature has an original audio.
            # First check whether the ORIG_AUDIO_DIR exists, if not then skip
            if not os.path.exists(ORIG_AUDIO_DIR):
                logger.warning(
                    f"Directory {ORIG_AUDIO_DIR} does not exist. Extract audio files from the game to this dir to detect whether a creature has an original audio in the game. Modify the directory in the script if the audio files are located elsewhere."
                )
            else:
                # Original audio files are named by appending a number and .wav to the creature name.
                # For example, NALIN01.WAV, NALIN02.WAV, etc.
                # Check if the creature has an original audio in the game.
                originalAudioPaths = original_audio_paths_getter(creature_id)
                if len(originalAudioPaths) > 0:
                    logger.info(
                        f"Creature {creature_id} has {len(originalAudioPaths)} original audios in the game."
                    )
                    copy_and_concat_audio(creature_id, originalAudioPaths)
                    results["creatures_with_original_audio"].append(creature_id)
                    continue
                # Sometimes (often) the original audio files are not named exactly the same as the creature name.
                # In such cases, the creature may still have an original audio in the game.
                # Remove the last char from the name and try again. We only try this once.
                alt_id = creature_id[:-1]
                logger.info(
                    f"Creature {creature_id} has no original audio in the game. Checking if {alt_id} has original audio in the game."
                )
                # Make sure altName does not refer to another creature
                if alt_id not in creatures:
                    originalAudioPaths = original_audio_paths_getter(alt_id)
                    if len(originalAudioPaths) > 0:
                        logger.info(
                            f"Creature {alt_id} has {len(originalAudioPaths)} original audios in the game."
                        )
                        copy_and_concat_audio(alt_id, originalAudioPaths)
                        results["creatures_with_original_audio"].append(alt_id)
                        continue
                    else:
                        logger.info(
                            f"No original audio found for {creature_id} or {alt_id}."
                        )

            # Using a random voice from the available voices for the gender in naturalReaderVoices
            if creature_id not in creatures:
                logger.warning(f"{creature_id} not found in creatures. Skipping.")
                results["unprocessable_creatures"].append(creature_id)
                continue

            subDirCreature = creatures[creature_id]
            gender = subDirCreature.get("gender")

            if gender not in ["male", "female"]:
                logger.warning(
                    f"Invalid gender '{gender}' for creature {creature_id}. Skipping."
                )
                results["unprocessable_creatures"].append(creature_id)
                continue

            if subDirCreature["name"] in companions.values():
                logger.info(
                    f"Creature creature_id '{creature_id}' found in companions. Skipping."
                )
                continue

            availableVoices = naturalReaderVoices.get(gender, {})
            if not availableVoices:
                logger.warning(
                    f"No available voices for gender '{gender}' in naturalReaderVoices. Skipping."
                )
                continue

            while True:
                picked_voices = set()
                while True:
                    voiceName, voiceLocale = random.choice(
                        list(availableVoices.items())
                    )
                    if voiceName not in picked_voices:
                        break

                logger.info(
                    f"Calling getSoundsForCreature for creature: {creature_id} with voice {voiceName} ({voiceLocale.lower()})"
                )

                cur_voice = {
                    "locale": voiceLocale.lower(),
                    "platform": "naturalReaders",
                    "voice": voiceName,
                }

                sample = getSoundsForCreature(
                    creature_id,
                    cur_voice,
                    1,
                )[0]

                # Auto play the audio
                command = f'cmd.exe /c "C:\\Program Files (x86)\\Windows Media Player\\wmplayer.exe" "D:\\VoicesVoicesExtravaganza\\bg\\vveBG\\WAV\\{sample}.wav" '
                os.system(command)

                # Ask for satisfication
                userChoice = askUserForVoice()

                # Satisfied
                if userChoice == "n":
                    results["new_voices"][creature_id] = cur_voice
                    break

                # Not satisfied
                # Delete wav file
                filename = f"{sample}.wav"
                filePath = os.path.join(WAV_DIR, filename)
                if os.path.exists(filePath):
                    os.remove(filePath)
                    logger.info(f"Deleted {filePath}")

                # Repick
                if userChoice == "y":
                    # Record the voice so that we don't pick it again
                    picked_voices.add(voiceName)

                    if len(picked_voices) == len(availableVoices):
                        logger.warning(
                            f"Exhausted all available voices for {creature_id}."
                        )

                # Store for manual processing
                if userChoice == "m" or len(picked_voices) == len(availableVoices):
                    logger.info(f"{creature_id} stored for manual processing.")
                    results["unprocessable_creatures"].append(creature_id)
                    break

            limit = limit - 1
    new_voices = results["new_voices"]
    for creature_id, voice in new_voices.items():
        logger.info(f"Getting sounds for creature: {creature_id}")
        getSoundsForCreature(
            creature_id,
            voice,
        )

    # Store the results into a json file appended with the current timestamp
    with open(
        f"audit_results_{datetime.now().strftime('%Y%m%d%H%M%S')}.json", "w"
    ) as f:
        json.dump(results, f, indent=4)
    logger.info(f"Audit completed. Processed {limit} creatures.")
    logger.info(results)
    logger.info(
        f"Results stored in audit_results_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
    )

    # Store unprompted creatures into onHold.json
    exempt.extend(results["unprocessable_creatures"])
    with open("static/onHold.json", "w") as f:
        json.dump(exempt, f, indent=4)

    # Store new voices in voices.json
    voices.update(results["new_voices"])
    # sort the voices by creature_id
    with open("static/voices.json", "w") as f:
        json.dump(dict(sorted(voices.items())), f, indent=2)


def askUserForVoice():
    while True:
        userInput = (
            input(
                "Do you want to randomly pick another voice?\n[Y]es   [N]o    [M]anual: "
            )
            .strip()
            .lower()
        )
        if userInput in ["y", "n", "m"]:
            return userInput
        print("Invalid input. Please enter 'y' or 'n'.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Auto audit some voices for creatures."
    )
    parser.add_argument(
        "-n", "--number", type=int, required=True, help="How many creatures to audit"
    )

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()

    number = args.number

    auditCreatures(number)
