#!/bin/bash

# stop execution when anything goes wrong
set -e

# create venv if not exist
if [ ! -d "./venv" ]
then
    echo "๐ถ Initializing virtual environment"
    python -m venv ./venv
    echo "๐ถ Virtual environment initialized"
fi

echo "๐ถ Activating virtual environment"
source ./venv/bin/activate
echo "๐ถ Virtual environment activated"

echo "๐ถ Assigning environment variables"
export APP_HTTP_PORT=8080
export APP_RESPONSE="ๆฒใใใใซๆบถใใฆใใใใใซ. ไบไบบใ ใใฎ็ฉบใๅบใใๅคใซ"
echo "๐ถ Environment variables assigned"

echo "๐ถ Starting application"
python main.py