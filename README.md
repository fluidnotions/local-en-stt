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
# Model configuration
WHISPER_MODEL=small

# Post-processing configuration
DEFAULT_FILLER_WORDS=um,uh,like,you know,I mean,actually,basically,literally
CUSTOM_FILLER_WORDS=sort of,kind of,anyway
WORD_REPLACEMENTS=thier=their,youre=you're,wont=won't,cant=can't
CAPITALIZE_FIRST=true
ADD_FINAL_PUNCTUATION=true
```

### Model Configuration
- `WHISPER_MODEL` selects the Whisper model size to load (`small` by default). Options include `tiny`, `base`, `small`, `medium`, and `large`.

### Post-processing Configuration
- `DEFAULT_FILLER_WORDS` is a comma-separated list of common filler words to be removed. You can modify this list to keep or remove specific default fillers.
- `CUSTOM_FILLER_WORDS` is an optional comma-separated list of additional filler words to be removed.
- `WORD_REPLACEMENTS` is a comma-separated list of word replacements in the format `wrong=right`. This helps correct commonly misrecognized words or add proper formatting (like apostrophes).
- `CAPITALIZE_FIRST` when set to `true` (default), capitalizes the first letter of the transcribed text.
- `ADD_FINAL_PUNCTUATION` when set to `true` (default), adds a period at the end of the text if no punctuation is present.

## Usage

Run the script:

```bash
python whisper_hotkey.py
```

Press and hold the left Ctrl key, dictate your text, and release the key when you're done.
Your speech will be transcribed and typed into the active input field after basic formatting.

The script automatically downloads the selected Whisper model if it's not
already cached. Transcription is performed in English only.

The script is configured to use FP32 precision (rather than FP16) to ensure compatibility with CPU-only systems.

## Customizing Post-Processing

You can customize how the transcribed text is processed by modifying the following settings in your `.env` file:

### Filler Word Removal

The script removes common filler words to produce cleaner transcriptions. You can customize this in two ways:

1. Modify `DEFAULT_FILLER_WORDS` to change the built-in list of filler words:
   ```
   DEFAULT_FILLER_WORDS=um,uh,hmm,like
   ```
   Setting this to empty (`DEFAULT_FILLER_WORDS=`) will disable the default filler removal.

2. Add your own custom filler words with `CUSTOM_FILLER_WORDS`:
   ```
   CUSTOM_FILLER_WORDS=sort of,kind of,you see
   ```

### Word Replacement

You can define replacements for words that are commonly misrecognized by the model or need specific formatting:

```
WORD_REPLACEMENTS=thier=their,youre=you're,api=API,commandline=command line
```

Each replacement pair is in the format `wrong=right` and separated by commas. This feature is useful for:

- Correcting common spelling errors in the transcription
- Adding apostrophes that might be missing
- Fixing technical terms or acronyms
- Formatting domain-specific terminology

### Text Formatting

You can control automatic text formatting:

- To disable automatic capitalization of the first letter:
  ```
  CAPITALIZE_FIRST=false
  ```

- To disable automatic addition of a period at the end:
  ```
  ADD_FINAL_PUNCTUATION=false
  ```

This allows you to customize the output text according to your specific needs and preferences.
