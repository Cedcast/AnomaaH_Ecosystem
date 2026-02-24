#!/bin/bash

# Build Android APK using Docker
# This avoids needing Android Studio or SDK installation
# Optimized for low-spec PCs

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Building Docker image for Android APK build..."
echo "Note: This process uses Docker to reduce load on your PC"
docker build -t android-apk-builder -f "$SCRIPT_DIR/build-apk.dockerfile" "$SCRIPT_DIR"

echo "Running Gradle assembleDebug inside container..."
echo "Building with optimized settings for low-spec machines..."
docker run --rm \
  -v "$SCRIPT_DIR/rider-app":/workspace \
  -w /workspace \
  android-apk-builder \
  "chmod +x ./gradlew && ./gradlew assembleDebug --no-daemon --max-workers=2"

echo "APK build completed!"
echo "Output: $SCRIPT_DIR/rider-app/build/outputs/apk/debug/"
