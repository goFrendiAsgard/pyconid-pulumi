#!/bin/bash

# stop execution when anything goes wrong
set -e

echo "🐶 Build image gofrendi/sample-app"
docker build -t gofrendi/sample-app .
echo "🐶 Image gofrendi/sample-app built"

echo "🐶 Push image gofrendi/sample-app"
docker push gofrendi/sample-app
echo "🐶 Image pushed"