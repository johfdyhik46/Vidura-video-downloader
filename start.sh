#!/bin/bash
pip install -r requirements.txt || { echo "pip install failed"; exit 1; }
python vidura.py
