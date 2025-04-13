#!/bin/bash
# Check if ffmpeg is already installed
if ! command -v ffmpeg &> /dev/null; then
    echo "ffmpeg not found. Render does not support apt-get in build environment."
    echo "Please ensure ffmpeg is available in the environment or use a custom Docker image."
    exit 1
fi
pip install -r requirements.txt || { echo "pip install failed"; exit 1; }
python vidura.py
