import os
import re
import argparse
import importlib
import sys
from utils.utilities import getVoice, WAV_DIR, TXT_DIR
from utils.logging_config import logger

wordFixes = {
    "Gorion": "Grraion",
    "Xzar": "Zar",
    "ye": "you",
    "Ye": "You",
    "ye're": "you're",
    "Ye're": "You're",
    "ye've": "you've",
    "Ye've": "You've",
    "ye'll": "you'll",
    "Ye'll": "You'll",
    "ye'd": "you'd",
    "Ye'd": "You'd",
    "te": "to",
    "Te": "To",
}

# These words are commonly spoken by the NPC when hostile,
# and are printed out in the console when you click on the talk button and then click the NPC
# however, even if they have sound files, they are not played when the words are spoken
hostileWords = (
    "I'll not have you near me",
    "I'll not speak a word after what you did",
)


def fix_words(words: str):
    words = re.sub(r"<[^>]+>, ", "", words)
    words = re.sub(r"<[^>]+>. ", "", words)
    words = re.sub(r"<[^>]+>\? ", "", words)
    words = re.sub(r"<[^>]+>! ", "", words)
    words = re.sub(r" <[^>]+>", "", words)
    for key, value in wordFixes.items():
        words = re.sub(rf"\b{re.escape(key)}\b", value, words)
    return words


def extractNumber(txtName):
    # Split the string by underscores
    parts = txtName.split("_")

    # Check if there are enough parts to extract the number
    if len(parts) >= 3:
        # Extract and return the number between the first and second underscores
        return parts[1]
    else:
        # Return None or an appropriate message if the format is incorrect
        return None


def wavExists(txtFileName: str):
    # e.g. "ABELA_2682_Destiny or no... I a [ABELA01].txt
    # wav already exists in game
    if txtFileName[-5] == "]":
        return True

    # wavs are in WAV_DIR
    number = extractNumber(txtFileName)
    wavFilepath = f"{WAV_DIR}/{number}.wav"
    return os.path.exists(wavFilepath)


def getSoundsForCreature(creatureId: str, voice=None):
    logger.info(f"Getting sounds for creature with ID {creatureId}")
    dir = f"{TXT_DIR}/{creatureId}"
    try:
        for filename in os.listdir(dir):
            if (not filename.endswith(".txt")) or wavExists(filename):
                continue
            filepath = os.path.join(dir, filename)

            with open(filepath, "r", encoding="utf-8") as file:
                words = file.readline()

                if words.startswith(hostileWords):
                    continue

                words = fix_words(words)
                if voice is None:
                    voice = getVoice(creatureId)
                number = extractNumber(filename)
                platform = voice["platform"]

                logger.info(f"Getting sound for line {number}: {words}")

                module_path = f"voiceGetters.{platform}"

                # Dynamically import the module
                module = importlib.import_module(module_path)
                # Call the getSoundForLine function from the module
                getattr(module, "getSoundForLine")(words, number, voice)
    except ImportError:
        raise ValueError(f"Unsupported platform: {platform}")
    except AttributeError:
        raise ValueError(
            f"The module {module_path} does not have the function 'getSoundForLine'"
        )
    except Exception as e:
        logger.error(f"{e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process some creatures.")
    parser.add_argument(
        "-c", "--creature", type=str, required=True, help="The name of the creature"
    )

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()

    creature = args.creature

    getSoundsForCreature(creature)
