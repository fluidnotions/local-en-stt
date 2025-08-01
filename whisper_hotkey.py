#!/usr/bin/env python3

import os
import re
import tempfile
import time
from threading import Event, Thread

import numpy
import pyautogui
import sounddevice as sd
import soundfile as sf
import whisper
from dotenv import load_dotenv
from pynput import keyboard

load_dotenv()

MODEL_SIZE = os.getenv("WHISPER_MODEL", "small")

# Get default filler words from .env or use built-in defaults
DEFAULT_FILLER_WORDS = os.getenv("DEFAULT_FILLER_WORDS", "um,uh,like,you know,I mean,actually,basically,literally")

# Get custom filler words from .env if specified
CUSTOM_FILLER_WORDS = os.getenv("CUSTOM_FILLER_WORDS", "")

# Parse default and custom filler words (comma-separated)
DEFAULT_FILLER_WORDS = [word.strip() for word in DEFAULT_FILLER_WORDS.split(",") if word.strip()]
CUSTOM_FILLER_WORDS = [word.strip() for word in CUSTOM_FILLER_WORDS.split(",") if word.strip()]

# Get post-processing settings
CAPITALIZE_FIRST = os.getenv("CAPITALIZE_FIRST", "true").lower() == "true"
ADD_FINAL_PUNCTUATION = os.getenv("ADD_FINAL_PUNCTUATION", "true").lower() == "true"

# Get word replacements from .env if specified
WORD_REPLACEMENTS = os.getenv("WORD_REPLACEMENTS", "")

# Parse word replacements (format: "wrong=right,another=correct")
REPLACEMENT_DICT = {}
for pair in WORD_REPLACEMENTS.split(","):
    pair = pair.strip()
    if pair and "=" in pair:
        wrong, right = pair.split("=", 1)
        REPLACEMENT_DICT[wrong.strip()] = right.strip()


def load_whisper_model(size: str) -> whisper.Whisper:
    """Load the Whisper model, downloading it if necessary."""
    print(f"Loading Whisper model '{size}' (download if missing)...")
    return whisper.load_model(size)


model = load_whisper_model(MODEL_SIZE)


def post_process(text: str) -> str:
    """Perform cleanup and formatting on the transcribed text.

    This function applies several transformations based on configuration:
    1. Removes filler words (from both DEFAULT_FILLER_WORDS and CUSTOM_FILLER_WORDS)
    2. Applies word replacements (from WORD_REPLACEMENTS)
    3. Capitalizes the first letter (if CAPITALIZE_FIRST is true)
    4. Adds final punctuation if missing (if ADD_FINAL_PUNCTUATION is true)
    """
    text = text.strip()
    if not text:
        return ""

    # Combine default and custom filler words
    filler_words = DEFAULT_FILLER_WORDS.copy()
    filler_words.extend(CUSTOM_FILLER_WORDS)

    # Replace filler words with an empty string
    for filler in filler_words:
        text = text.replace(f" {filler} ", " ")  # Remove fillers surrounded by spaces
        text = text.replace(f" {filler}.", ".")  # Remove fillers followed by a period
        text = text.replace(f" {filler},", ",")  # Remove fillers followed by a comma
        # Handle case where filler starts the sentence
        if text.lower().startswith(f"{filler} "):
            text = text[len(filler) + 1:]

    # Remove repeated spaces
    while "  " in text:
        text = text.replace("  ", " ")

    # Apply word replacements for commonly misrecognized words
    for wrong_word, right_word in REPLACEMENT_DICT.items():
        # Replace whole words with word boundaries
        text = re.sub(r'\b' + re.escape(wrong_word) + r'\b', right_word, text, flags=re.IGNORECASE)

    # Capitalize the first letter if configured and text is not empty
    if CAPITALIZE_FIRST and text:
        text = text[0].upper() + text[1:]

    # Ensure the sentence ends with appropriate punctuation if configured
    if ADD_FINAL_PUNCTUATION and text and text[-1] not in ".!?":
        text += "."

    return text


def record_audio(sample_rate: int = 16000) -> str:
    """Record audio from the microphone while left Ctrl key is held down."""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        # Create a buffer to store audio data
        audio_chunks = []
        stop_event = Event()

        # Function to collect audio data in chunks
        def callback(indata, frames, time, status):
            if status:
                print(f"Error in audio recording: {status}")
            audio_chunks.append(indata.copy())

        # Start the recording stream
        stream = sd.InputStream(samplerate=sample_rate, channels=1, callback=callback)
        stream.start()

        print("Recording while left Ctrl is held down...")

        # Wait until left Ctrl is released
        with keyboard.Events() as events:
            for event in events:
                if isinstance(event, keyboard.Events.Release) and event.key == keyboard.Key.ctrl_l:
                    break

        # Stop the recording stream
        stream.stop()
        stream.close()

        # Combine all audio chunks and save to file
        if audio_chunks:
            recording = numpy.concatenate(audio_chunks, axis=0)
            sf.write(tmp.name, recording, sample_rate)
            print(f"Recorded {len(recording)/sample_rate:.2f} seconds of audio")
            return tmp.name
        else:
            print("No audio recorded")
            return ""



def transcribe_file(path: str) -> str:
    # Set fp16=False to prevent FP16 warning on CPU
    result = model.transcribe(path, language="en", fp16=False)
    return result["text"].strip()


def on_activate():
    print("Left Ctrl pressed. Starting to record...")
    audio_path = record_audio()
    if audio_path and os.path.exists(audio_path):
        print("Transcribing...")
        text = transcribe_file(audio_path)
        os.remove(audio_path)
        cleaned = post_process(text)
        if cleaned:
            print(f"Typing: {cleaned}")
            pyautogui.typewrite(cleaned)
        else:
            print("No speech detected.")
    else:
        print("No audio file to transcribe.")


def main() -> None:
    print(f"Loaded whisper model '{MODEL_SIZE}'")
    print("Press and hold left Ctrl key to start recording. Release to stop and transcribe.")

    # Listen for the left Ctrl key press
    with keyboard.Listener(
        on_press=lambda key: on_activate() if key == keyboard.Key.ctrl_l else None
    ) as listener:
        listener.join()


if __name__ == "__main__":
    main()
