import os
import tempfile

import pyautogui
import sounddevice as sd
import soundfile as sf
import whisper
from dotenv import load_dotenv
from pynput import keyboard

load_dotenv()

HOTKEY = os.getenv("HOTKEY", "<cmd>+<shift>+t")
MODEL_SIZE = os.getenv("WHISPER_MODEL", "small")
RECORD_SECONDS = int(os.getenv("RECORD_SECONDS", "5"))

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


def record_audio(duration: int, sample_rate: int = 16000) -> str:
    """Record audio from the microphone and save to a temporary WAV file."""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        print(f"Recording for {duration} seconds...")
        recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1)
        sd.wait()
        sf.write(tmp.name, recording, sample_rate)
        return tmp.name


def transcribe_file(path: str) -> str:
    result = model.transcribe(path, language="en")
    return result["text"].strip()


def on_activate():
    print("Hotkey pressed. Listening...")
    audio_path = record_audio(RECORD_SECONDS)
    print("Transcribing...")
    text = transcribe_file(audio_path)
    os.remove(audio_path)
    cleaned = post_process(text)
    if cleaned:
        print(f"Typing: {cleaned}")
        pyautogui.typewrite(cleaned)
    else:
        print("No speech detected.")


def main() -> None:
    print(f"Loaded whisper model '{MODEL_SIZE}' and waiting for hotkey '{HOTKEY}'.")
    with keyboard.GlobalHotKeys({HOTKEY: on_activate}) as h:
        h.join()


if __name__ == "__main__":
    main()
