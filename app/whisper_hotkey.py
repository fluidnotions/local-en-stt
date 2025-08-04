#!/usr/bin/env python3

import os
import re
import tempfile
import argparse
import tkinter as tk
from threading import Event, Thread
from pathlib import Path
from queue import Queue

import numpy
import pyautogui
import sounddevice as sd
import soundfile as sf
import whisper
from dotenv import load_dotenv
from pynput import keyboard

# Import UI implementations
from .ui.ui_interface import WhisperHotkeyUI
from .ui.gui_implementation import WhisperHotkeyGUI
from .ui.terminal_implementation import WhisperHotkeyTerminal

# Create a message queue for UI output
message_queue = Queue()

# Store original print function
original_print = print

# Custom print function that logs to both console and UI
def log_message(message):
    """Send message to both console and UI."""
    original_print(message)
    message_queue.put(message)

# Override the default print function
print = log_message

# App configuration
APP_NAME = "WhisperHotkey"
APP_DIR = Path.home() / f".{APP_NAME}"
ENV_FILE = APP_DIR / ".env"

# Default environment configuration
DEFAULT_ENV = """
# Model configuration
WHISPER_MODEL=small

# Post-processing configuration
FILLER_WORDS=um,uh,like,you know,I mean,actually,basically,literally,sort of,kind of,anyway
WORD_REPLACEMENTS=gooey=gui
CAPITALIZE_FIRST=true
ADD_FINAL_PUNCTUATION=true
"""

# Text processing module
class TextProcessor:
    def __init__(self):
        self.replacements = None
        self.add_punctuation = None
        self.capitalize_first = None
        self.filler_words = None
        self.reload_config()

    def reload_config(self):
        """Load text processing configuration from environment variables"""
        # Get filler words from .env or use built-in defaults
        fillers = os.getenv("FILLER_WORDS", "um,uh,like,you know,I mean,actually,basically,literally,sort of,kind of,anyway")

        # Parse filler words (comma-separated)
        self.filler_words = [word.strip() for word in fillers.split(",") if word.strip()]

        # Get formatting settings
        self.capitalize_first = os.getenv("CAPITALIZE_FIRST", "true").lower() == "true"
        self.add_punctuation = os.getenv("ADD_FINAL_PUNCTUATION", "true").lower() == "true"

        # Parse word replacements
        replacements = os.getenv("WORD_REPLACEMENTS", "")
        self.replacements = {}
        for pair in replacements.split(","):
            pair = pair.strip()
            if pair and "=" in pair:
                wrong, right = pair.split("=", 1)
                self.replacements[wrong.strip()] = right.strip()

    def process(self, text):
        """Apply all text processing rules to the input text"""
        text = text.strip()
        if not text:
            return ""

        # Apply filler word removal
        text = self._remove_fillers(text)

        # Apply word replacements
        text = self._replace_words(text)

        # Apply formatting
        text = self._format_text(text)

        return text

    def _remove_fillers(self, text):
        """Remove filler words from the text"""
        # Process text for filler word removal
        for filler in self.filler_words:
            # Prepare the pattern to match filler words case-insensitively
            # Note: Using regex with word boundaries to ensure we match whole filler phrases
            pattern = re.compile(r'\b' + re.escape(filler) + r'\b', re.IGNORECASE)

            # Remove the filler words - including handling punctuation that might follow
            text = pattern.sub('', text)

            # Also handle the start of sentence case explicitly
            if text.lower().startswith(filler.lower() + ' '):
                text = text[len(filler) + 1:]

        # Clean up any resulting artifacts from removal
        # Fix double spaces
        while "  " in text:
            text = text.replace("  ", " ")

        # Fix spaces before punctuation
        for punct in ['.', ',', '!', '?', ':', ';']:
            text = text.replace(f" {punct}", punct)

        # Fix leading spaces
        text = text.strip()

        return text

    def _replace_words(self, text):
        """Apply word replacements"""
        for wrong_word, right_word in self.replacements.items():
            # Replace whole words with word boundaries
            text = re.sub(r'\b' + re.escape(wrong_word) + r'\b', right_word, text, flags=re.IGNORECASE)
        return text

    def _format_text(self, text):
        """Apply text formatting rules"""
        # Capitalize the first letter if configured and text is not empty
        if self.capitalize_first and text:
            text = text[0].upper() + text[1:]

        # Ensure the sentence ends with appropriate punctuation if configured
        if self.add_punctuation and text and text[-1] not in ".!?":
            text += "."

        return text

# Initialize app directory and config file
def init_app_config():
    """Create an app directory and default configuration if they don't exist."""
    if not APP_DIR.exists():
        APP_DIR.mkdir(parents=True, exist_ok=True)
        print(f"Created application directory: {APP_DIR}")

    if not ENV_FILE.exists():
        with open(ENV_FILE, 'w') as f:
            f.write(DEFAULT_ENV.strip())
        print(f"Created default configuration file: {ENV_FILE}")
        print(f"You can edit this file to customize settings.")
    else:
        print(f"Using existing configuration: {ENV_FILE}")

# The WhisperHotkeyGUI class has been moved to gui_implementation.py

def load_whisper_model(size: str) -> whisper.Whisper:
    """Load the Whisper model, downloading it if necessary."""
    print(f"Loading Whisper model '{size}' (download if missing)...")
    return whisper.load_model(size)

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

        # Wait until the left Ctrl is released
        with keyboard.Events() as events:
            for event in events:
                if isinstance(event, keyboard.Events.Release) and event.key == keyboard.Key.ctrl_l:
                    break

        # Stop the recording stream
        stream.stop()
        stream.close()

        # Combine all audio chunks and save to a file
        if audio_chunks:
            recording = numpy.concatenate(audio_chunks, axis=0)
            sf.write(tmp.name, recording, sample_rate)
            print(f"Recorded {len(recording)/sample_rate:.2f} seconds of audio")
            return tmp.name
        else:
            print("No audio recorded")
            return ""

def transcribe_file(path: str) -> str:
    """Transcribe an audio file using a Whisper model"""
    # Set fp16=False to prevent FP16 warning on CPU
    result = model.transcribe(path, language="en", fp16=False)
    return result["text"].strip()

def on_activate(text_processor):
    """Handle activation when the Ctrl key is pressed"""
    if hasattr(app, 'update_status'):
        app.update_status("Left Ctrl pressed. Starting to record...")
    print("Left Ctrl pressed. Starting to record...")

    audio_path = record_audio()
    if audio_path and os.path.exists(audio_path):
        if hasattr(app, 'update_status'):
            app.update_status("Transcribing...")
        print("Transcribing...")
        text = transcribe_file(audio_path)
        os.remove(audio_path)

        # Apply text processing
        cleaned = text_processor.process(text)

        if cleaned:
            print(f"Typing: {cleaned}")
            pyautogui.typewrite(cleaned)
            if hasattr(app, 'update_status'):
                app.update_status("Ready. Press and hold left Ctrl to record.")
        else:
            print("No speech detected.")
            if hasattr(app, 'update_status'):
                app.update_status("No speech detected. Press and hold left Ctrl to try again.")
    else:
        print("No audio file to transcribe.")
        if hasattr(app, 'update_status'):
            app.update_status("No audio recorded. Press and hold left Ctrl to try again.")

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description=f"{APP_NAME} - Speech-to-Text Tool")
    parser.add_argument(
        "--terminal", 
        action="store_true", 
        help="Run in terminal mode instead of GUI mode"
    )
    return parser.parse_args()

def main() -> None:
    """Main application entry point"""
    global app, model

    # Parse command line arguments
    args = parse_arguments()

    # Initialize the app configuration
    init_app_config()

    # Load environment variables
    load_dotenv(ENV_FILE)

    # Get model size from config
    model_size = os.getenv("WHISPER_MODEL", "small")

    # Initialize the text processor
    text_processor = TextProcessor()

    print(f"Loading Whisper Hotkey application...")
    print(f"Using configuration from: {ENV_FILE}")

    # Load the Whisper model
    model = load_whisper_model(model_size)
    print(f"Loaded Whisper model '{model_size}'")
    print("Press and hold left Ctrl key to start recording. Release to stop and transcribe.")

    # Create the appropriate UI implementation based on arguments
    if args.terminal:
        print("Running in terminal mode")
        app = WhisperHotkeyTerminal(APP_NAME, ENV_FILE)
    else:
        print("Running in GUI mode")
        # Create the GUI implementation
        app = WhisperHotkeyGUI(APP_NAME, ENV_FILE)

    # Start a keyboard listener in a separate thread
    listener = keyboard.Listener(
        on_press=lambda key: on_activate(text_processor) if key == keyboard.Key.ctrl_l else None
    )
    listener.daemon = True
    listener.start()

    # Start the UI
    app.start()

if __name__ == "__main__":
    main()

