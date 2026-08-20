#!/bin/bash
set -e
echo "Building SAIF Backend..."
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
echo "Build complete."
