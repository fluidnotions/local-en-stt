# Local English Speech-to-Text

This project provides a Python application that uses OpenAI's Whisper model to dictate spoken English directly into the currently focused input field on macOS. The app listens for a keyboard shortcut, records a short audio clip, transcribes it with Whisper, performs configurable cleanup, and types the resulting text.

## Features

- Speech-to-text dictation with OpenAI's Whisper model
- Automatic text formatting and cleanup
- Customizable filler word removal
- Word replacement for common transcription errors
- Simple GUI with status display and logging
- Configuration stored in user's home directory

## Installation

### Option 1: Run from Source

1. Install Python 3.9 or newer
2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python whisper_hotkey.py
   ```

### Option 2: Create an Executable

1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```
2. Create a standalone executable:
   ```bash
   pyinstaller --onefile --windowed whisper_hotkey.py
   ```
3. The executable will be created in the `dist` directory
4. Double-click the executable to run it

## Usage

1. The application opens with a GUI window showing status and logs
2. Press and hold the left Ctrl key
3. Speak your text
4. Release the Ctrl key when done
5. The transcribed text will be typed at your cursor position

On the first run, the app automatically:
- Creates a configuration folder in your home directory (`~/.WhisperHotkey`)
- Generates a default configuration file
- Downloads the selected Whisper model if not already cached

## Configuration

The app automatically creates a configuration file at `~/.WhisperHotkey/.env`. You can edit this file directly or use the "Edit Configuration" button in the application.

```bash
# Model configuration
WHISPER_MODEL=small

# Post-processing configuration
DEFAULT_FILLER_WORDS=um,uh,like,you know,I mean,actually,basically,literally
CUSTOM_FILLER_WORDS=sort of,kind of,anyway
WORD_REPLACEMENTS=thier=their,youre=you're,wont=won't,cant=can't
CAPITALIZE_FIRST=true
ADD_FINAL_PUNCTUATION=true
```

### Available Settings

#### Model Selection
- `WHISPER_MODEL`: Choose model size (`tiny`, `base`, `small`, `medium`, or `large`)

#### Text Processing
- `DEFAULT_FILLER_WORDS`: Common filler words to remove (comma-separated)
- `CUSTOM_FILLER_WORDS`: Additional filler words to remove
- `WORD_REPLACEMENTS`: Automatic word corrections in format `wrong=right`
- `CAPITALIZE_FIRST`: Capitalize the first letter (`true`/`false`)
- `ADD_FINAL_PUNCTUATION`: Add period if missing (`true`/`false`)

## Customization Examples

### Filler Word Removal

Modify the default list or add your own:
```
DEFAULT_FILLER_WORDS=um,uh,hmm,like
CUSTOM_FILLER_WORDS=sort of,kind of,you see
```

### Word Replacement

Define replacements for commonly misrecognized words:
```
WORD_REPLACEMENTS=thier=their,youre=you're,api=API,commandline=command line
```

This is useful for:
- Correcting common spelling errors
- Adding missing apostrophes
- Fixing technical terms or acronyms
- Formatting domain-specific terminology

### Text Formatting

Control automatic formatting:
```
CAPITALIZE_FIRST=false
ADD_FINAL_PUNCTUATION=false
```

## Technical Notes

- Transcription is performed in English only
- FP32 precision is used instead of FP16 for CPU compatibility
- Configuration is stored separately from the executable for easy customization
