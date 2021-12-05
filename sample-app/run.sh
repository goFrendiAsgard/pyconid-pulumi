#!/bin/bash

# stop execution when anything goes wrong
set -e

# create venv if not exist
if [ ! -d "./venv" ]
then
    echo "🐶 Initializing virtual environment"
    python -m venv ./venv
    echo "🐶 Virtual environment initialized"
fi

echo "🐶 Activating virtual environment"
source ./venv/bin/activate
echo "🐶 Virtual environment activated"

echo "🐶 Assigning environment variables"
export APP_HTTP_PORT=8080
export APP_RESPONSE="沈むように溶けてゆくように. 二人だけの空が広がる夜に"
echo "🐶 Environment variables assigned"

echo "🐶 Starting application"
python main.py