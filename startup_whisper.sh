#!/bin/bash

# Path to the conda installation
export PATH="/opt/anaconda3/bin:$PATH"

# Source conda.sh to enable conda command
source /opt/anaconda3/etc/profile.d/conda.sh

# Navigate to the project directory
cd /Users/justinrobinson/Documents/personal/local-en-tts

# Activate the conda environment
conda activate raft

# Run the Python script
python whisper_hotkey.py