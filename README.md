# Local English Speech-to-Text

This project provides a small Python script that uses OpenAI's Whisper model
to dictate spoken English directly into the currently focused input field on
macOS. The script listens for a keyboard shortcut defined in a `.env` file,
records a short audio clip, transcribes it with Whisper, performs minimal
cleanup, and types the resulting text.

## Installation

1. Install Python 3.9 or newer.
2. Install the required Python packages:

```bash
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the project directory. Example:

```bash
HOTKEY=<cmd>+<shift>+t
WHISPER_MODEL=small
RECORD_SECONDS=5
```

- `HOTKEY` sets the keyboard shortcut that triggers recording.
- `WHISPER_MODEL` selects the Whisper model size to load (`small` by default).
- `RECORD_SECONDS` controls how long to record when the hotkey is pressed.

## Usage

Run the script:

```bash
python whisper_hotkey.py
```

Press the configured hotkey, dictate your text, and it will be transcribed
and typed into the active input field after basic formatting.
