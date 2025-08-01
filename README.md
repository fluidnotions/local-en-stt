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

1. Install Python 3.9 or newer
2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python whisper_hotkey.py
   ```

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
FILLER_WORDS=um,uh,like,you know,I mean,actually,basically,literally,sort of,kind of,anyway
WORD_REPLACEMENTS=thier=their,youre=you're,wont=won't,cant=can't
CAPITALIZE_FIRST=true
ADD_FINAL_PUNCTUATION=true
```

### Available Settings

#### Model Selection
- `WHISPER_MODEL`: Choose model size (`tiny`, `base`, `small`, `medium`, or `large`)

#### Text Processing
- `FILLER_WORDS`: Filler words to remove from transcription (comma-separated)
- `WORD_REPLACEMENTS`: Automatic word corrections in format `wrong=right`
- `CAPITALIZE_FIRST`: Capitalize the first letter (`true`/`false`)
- `ADD_FINAL_PUNCTUATION`: Add period if missing (`true`/`false`)

## Customization Examples

### Filler Word Removal

Customize the list of filler words to remove:
```
FILLER_WORDS=um,uh,hmm,like,sort of,kind of,you see
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
- Configuration is stored in the user's home directory for easy customization

## Running at Startup (macOS)

The application can be configured to start automatically when you log in to your Mac:

1. The startup configuration has been set up with the following files:
   - `/Users/justinrobinson/Documents/personal/local-en-tts/startup_whisper.sh`: A shell script that activates the conda environment and runs the application
   - `/Users/justinrobinson/Library/LaunchAgents/com.justinrobinson.whisperhotkey.plist`: A LaunchAgent that runs the shell script at login

2. The application will now start automatically when you log in to your Mac.

3. Logs are stored in:
   - `/Users/justinrobinson/Library/Logs/whisperhotkey.log`: Standard output
   - `/Users/justinrobinson/Library/Logs/whisperhotkey.err`: Error messages

4. To disable automatic startup:
   ```bash
   launchctl unload ~/Library/LaunchAgents/com.justinrobinson.whisperhotkey.plist
   ```

5. To enable automatic startup again:
   ```bash
   launchctl load ~/Library/LaunchAgents/com.justinrobinson.whisperhotkey.plist
   ```
