#!/usr/bin/env python3

import os
import re
import tempfile
import time
import shutil
import tkinter as tk
from tkinter import scrolledtext
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

# App configuration
APP_NAME = "WhisperHotkey"
APP_DIR = Path.home() / f".{APP_NAME}"
ENV_FILE = APP_DIR / ".env"

# Create a message queue for GUI output
message_queue = Queue()

# Default environment configuration
DEFAULT_ENV = """
# Model configuration
WHISPER_MODEL=small

# Post-processing configuration
DEFAULT_FILLER_WORDS=um,uh,like,you know,I mean,actually,basically,literally
CUSTOM_FILLER_WORDS=sort of,kind of,anyway
WORD_REPLACEMENTS=thier=their,youre=you're,wont=won't,cant=can't
CAPITALIZE_FIRST=true
ADD_FINAL_PUNCTUATION=true
"""

# Initialize app directory and config file
def init_app_config():
    """Create app directory and default configuration if they don't exist."""
    if not APP_DIR.exists():
        APP_DIR.mkdir(parents=True, exist_ok=True)
        log_message(f"Created application directory: {APP_DIR}")

    if not ENV_FILE.exists():
        with open(ENV_FILE, 'w') as f:
            f.write(DEFAULT_ENV.strip())
        log_message(f"Created default configuration file: {ENV_FILE}")
        log_message(f"You can edit this file to customize settings.")
    else:
        log_message(f"Using existing configuration: {ENV_FILE}")

# Initialize configuration
init_app_config()

# Load environment variables from app directory
load_dotenv(ENV_FILE)

# Get configuration values
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


    # GUI application for displaying logs
    class WhisperHotkeyGUI:
    def __init__(self, root):
        self.root = root
        self.root.title(f"{APP_NAME} - Speech-to-Text Tool")
        self.root.geometry("700x400")
        self.root.minsize(500, 300)

        # Create a frame for the log display
        frame = tk.Frame(root)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Status label
        self.status_label = tk.Label(frame, text="Ready. Press and hold left Ctrl to record.")
        self.status_label.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))

        # Create a scrolled text widget for logs
        self.log_display = scrolledtext.ScrolledText(frame, wrap=tk.WORD)
        self.log_display.pack(fill=tk.BOTH, expand=True)
        self.log_display.config(state=tk.DISABLED)

        # Create a frame for buttons
        button_frame = tk.Frame(root)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        # Button to open configuration file
        self.config_button = tk.Button(
            button_frame, 
            text="Edit Configuration", 
            command=self.open_config_file
        )
        self.config_button.pack(side=tk.LEFT, padx=5)

        # Status indicator
        self.status_indicator = tk.Label(
            button_frame,
            text="⚪ Idle",
            font=("Arial", 10)
        )
        self.status_indicator.pack(side=tk.RIGHT, padx=5)

        # Start polling for messages
        self.poll_messages()

    def poll_messages(self):
        """Check for new messages in the queue and update display."""
        try:
            while not message_queue.empty():
                message = message_queue.get_nowait()
                self.update_log(message)
        except Exception as e:
            self.update_log(f"Error polling messages: {e}")

        # Schedule the next poll
        self.root.after(100, self.poll_messages)

    def update_log(self, message):
        """Add a message to the log display."""
        self.log_display.config(state=tk.NORMAL)
        self.log_display.insert(tk.END, f"{message}\n")
        self.log_display.see(tk.END)  # Scroll to bottom
        self.log_display.config(state=tk.DISABLED)

    def update_status(self, status):
        """Update the status indicator."""
        self.status_label.config(text=status)

        if "recording" in status.lower():
            self.status_indicator.config(text="🔴 Recording", fg="red")
        elif "transcribing" in status.lower():
            self.status_indicator.config(text="🔄 Processing", fg="blue")
        else:
            self.status_indicator.config(text="⚪ Idle", fg="black")

    def open_config_file(self):
        """Open the configuration file for editing."""
        log_message(f"Opening configuration file: {ENV_FILE}")
        try:
            # On macOS, use 'open' command
            if os.name == 'posix':
                os.system(f"open {ENV_FILE}")
            # On Windows, use the default editor
            elif os.name == 'nt':
                os.system(f"start {ENV_FILE}")
            else:
                log_message(f"Please manually edit the config file at: {ENV_FILE}")
        except Exception as e:
            log_message(f"Error opening config file: {e}")

    # Custom print function that logs to both console and GUI
    def log_message(message):
    """Send message to both console and GUI."""
    print(message)
    message_queue.put(message)

    # Override the original print function for this module
    original_print = print
    print = log_message

    # Update on_activate to update GUI status
    def on_activate():
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
        cleaned = post_process(text)
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

    def main() -> None:
    global app

    print(f"Loading Whisper Hotkey application...")
    print(f"Using configuration from: {ENV_FILE}")
    print(f"Loaded whisper model '{MODEL_SIZE}'")
    print("Press and hold left Ctrl key to start recording. Release to stop and transcribe.")

    # Create the GUI
    root = tk.Tk()
    app = WhisperHotkeyGUI(root)

    # Start keyboard listener in a separate thread
    listener = keyboard.Listener(
        on_press=lambda key: on_activate() if key == keyboard.Key.ctrl_l else None
    )
    listener.daemon = True
    listener.start()

    # Start the GUI main loop
    root.mainloop()


if __name__ == "__main__":
    main()
