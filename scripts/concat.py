import argparse
import os
import subprocess
import sys
from utils.logging_config import logger
from utils.utilities import VOICELAB_DIR


def get_sample_rate(wav_file):
    result = subprocess.run(
        [
            "ffprobe",
            "-hide_banner",
            "-loglevel",
            "quiet",
            "-v",
            "error",
            "-select_streams",
            "a:0",
            "-show_entries",
            "stream=sample_rate",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            wav_file,
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return int(result.stdout.strip())


def get_duration(wav_file):
    result = subprocess.run(
        [
            "ffprobe",
            "-hide_banner",
            "-loglevel",
            "quiet",
            "-v",
            "error",
            "-select_streams",
            "a:0",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            wav_file,
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return float(result.stdout.strip())


def resample_wav(wav_file, target_rate, creature):
    base_name = os.path.basename(wav_file)
    output_file = os.path.join(VOICELAB_DIR, creature, f"resampled_{base_name}")
    subprocess.run(
        ["ffmpeg", "-i", wav_file, "-ar", str(target_rate), output_file],
        check=True,
    )
    return output_file


def create_silence_wav(creature, target_rate):
    # Create 1 second of silence wav file with the specified format
    subprocess.run(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "quiet",
            "-f",
            "lavfi",
            "-i",
            f"anullsrc=r={target_rate}:cl=mono",
            "-t",
            "1",
            f"{VOICELAB_DIR}/{creature}/silence.wav",
        ],
        check=True,
    )


def create_file_list(wav_files, creature):
    # Create a list of files to concatenate
    with open(f"{VOICELAB_DIR}/{creature}/files.txt", "w") as f:
        for wav_file in wav_files:
            base_name = os.path.basename(wav_file)
            f.write(f"file '{base_name}'\n")
            f.write("file 'silence.wav'\n")
        # Remove the last silence entry
        f.seek(f.tell() - len("file 'silence.wav'\n"), os.SEEK_SET)
        f.truncate()


def concatenate_files(creature):
    # Concatenate the files using ffmpeg with specified format
    subprocess.run(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "quiet",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            f"{VOICELAB_DIR}/{creature}/files.txt",
            "-ar",
            "22050",
            "-ac",
            "1",
            "-sample_fmt",
            "s16",
            "-c",
            "pcm_s16le",
            f"{VOICELAB_DIR}/{creature}/{creature}.wav",
        ],
        check=True,
    )


def do_concatenation(creature: str):
    # Get list of WAV files in current directory
    wav_files = [
        f
        for f in sorted(os.listdir(os.path.join(VOICELAB_DIR, creature)))
        if f.endswith(".WAV") and not f.startswith("resampled_")
    ]

    # Resample WAV files to 22 kHz if needed
    target_rate = 22050
    resampled_files = []

    for wav_file in wav_files:
        wav_file_path = os.path.join(VOICELAB_DIR, creature, wav_file)
        sample_rate = get_sample_rate(wav_file_path)
        duration = get_duration(wav_file_path)

        # if duration < 1.0:
        #     logger.info(
        #         f"Ignoring {wav_file_path} as its duration is less than 1 second."
        #     )
        #     continue

        if sample_rate != target_rate:
            resampled_file = resample_wav(wav_file_path, target_rate, creature)
            resampled_files.append(os.path.basename(resampled_file))
        else:
            resampled_files.append(wav_file)

    # Create silence.wav if it doesn't exist
    if not os.path.exists(f"{VOICELAB_DIR}/{creature}/silence.wav"):
        create_silence_wav(creature, target_rate)

    # Create the files.txt list
    create_file_list(resampled_files, creature)

    # Concatenate the files
    concatenate_files(creature)


def main():
    parser = argparse.ArgumentParser(description="Process some creatures.")
    parser.add_argument(
        "-c", "--creature", type=str, required=True, help="The name of the creature"
    )

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()

    do_concatenation(args.creature)


if __name__ == "__main__":
    main()
