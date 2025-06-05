#!/bin/env python3

import logging
import subprocess
from pathlib import Path

from openai import OpenAI

# Set up logging configuration
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def select_target() -> Path:
    """
    Select which video clip to generate a translation for by listing available files and selecting using numbers.
    On error, it should log an error and return an empty path.
    """
    logging.info("selecting target")

    video_files = list(Path("./to_transcribe/").glob("*.mp4"))
    if not video_files:
        logging.error("No video files found to transcribe.")
        return Path()

    logging.info("Available video files:")
    for idx, file in enumerate(video_files, start=1):
        logging.info(f"{idx}: {file.name}")

    selected_index = input("Enter the number of the video file to translate: ")
    try:
        selected_index = int(selected_index) - 1
        if 0 <= selected_index < len(video_files):
            target_file = video_files[selected_index]
            logging.info(f"Target selected: {target_file}")
            return target_file
        else:
            logging.error("Invalid selection.")
    except ValueError:
        logging.error("Invalid input.")

    return Path()


def split_audio_track(clip: Path) -> Path:
    """
    Split the audiotrack of the selected clip using ffmpeg or equivalent.
    Should catch exception if the clip is not found and return a path to
    the audio file, stored as a temporary file. The audio file should be logged.
    """
    from tempfile import NamedTemporaryFile

    logging.info("splitting audio track")
    audio_file_path = Path("/tmp") / f"{clip.stem}.mp3"

    try:
        subprocess.run(
            [
                "ffmpeg",
                "-i",
                str(clip),
                "-q:a",
                "0",
                "-map",
                "a",
                audio_file_path,
            ],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        stdout = e.stdout
        stderr = e.stderr
        logging.error(f"ffmpeg failed with stdout: {stdout}, stderr: {stderr}")
        if "Not overwriting" in stderr or "already exists" in stderr:
            logging.info("Audio file already exists, continuing")
        else:
            raise
    logging.info(f"audio track saved to: {audio_file_path}")
    return Path(audio_file_path)


def translate_and_save(audio_file_path: Path) -> Path:
    """
    Translate the audio file and lastly save the translation
    as a text document in the local directory './translations'.
    If error, it should log error and on success it should log the path to the translation
    """
    logging.info(f"translating and saving, using: {audio_file_path}")
    client = OpenAI()
    with open(audio_file_path, "rb") as audio_file:
        translation = client.audio.translations.create(
            model="whisper-1",
            file=audio_file,
        )

    translations_path = Path("./translations")
    translations_path.mkdir(exist_ok=True)
    save_path = translations_path / f"{audio_file_path.stem}_translation.txt"
    translation_dict = translation.to_dict()
    translation_text = translation_dict.get("text")
    if not translation_text:
        raise Exception(f"failed to find text in: {translation_dict}")

    translation_text = str(translation_text).replace(". ", ".\n")
    with open(save_path, "w") as f:
        f.write(translation_text)

    logging.info(f"Translation saved to: {save_path}")
    return save_path


if __name__ == "__main__":
    target = select_target()
    if not target.exists():
        logging.error("failed to find video clip to translate")
        exit(1)
    audio_file = split_audio_track(target)
    if not audio_file.exists():
        logging.error("failed to split audio from video clip")
        exit(1)

    translate_and_save(audio_file)
