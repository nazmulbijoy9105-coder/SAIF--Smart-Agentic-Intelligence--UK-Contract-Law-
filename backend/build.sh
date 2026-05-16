#!/usr/bin/env bash
set -o errexit

echo "====== SAIF Build Script ======"

# Check runtime.txt
if [ -f runtime.txt ]; then
    PY_VERSION=$(cat runtime.txt | tr -d '\r\n')
    echo "Python version from runtime.txt: $PY_VERSION"
fi

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

echo "====== Build Complete ======"
