#!/bin/bash
apt-get update || { echo "apt-get update failed"; exit 1; }
apt-get install -y ffmpeg || { echo "ffmpeg install failed"; exit 1; }
pip install -r requirements.txt || { echo "pip install failed"; exit 1; }
python vidura.py
