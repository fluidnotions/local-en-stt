#!/usr/bin/env python3

import os
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


def load_whisper_model(size: str) -> whisper.Whisper:
    """Load the Whisper model, downloading it if necessary."""
    print(f"Loading Whisper model '{size}' (download if missing)...")
    return whisper.load_model(size)


model = load_whisper_model(MODEL_SIZE)


def post_process(text: str) -> str:
    text = text.strip()
    if not text:
        return ""
    text = text[0].upper() + text[1:]
    if text[-1] not in ".!?":
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
    result = model.transcribe(path, language="en")
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
