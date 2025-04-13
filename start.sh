#!/bin/bash

set -e  # Exit on any error

echo "Updating apt..."
apt-get update || { echo "apt-get update failed"; exit 1; }

echo "Installing ffmpeg..."
apt-get install -y ffmpeg || { echo "ffmpeg install failed"; exit 1; }

echo "Installing Python dependencies..."
pip install -r requirements.txt || { echo "pip install failed"; exit 1; }

echo "Starting application..."
python vidura.py
