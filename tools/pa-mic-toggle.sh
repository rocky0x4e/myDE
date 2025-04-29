#!/bin/bash

# Get all microphone sources
MIC_SOURCES=$(pactl list short sources | grep input | cut -f1)

# Check if any sources are found
if [[ -z "$MIC_SOURCES" ]]; then
  echo "No microphone sources found."
  exit 1
fi

# Loop through each microphone source and mute it
for SOURCE in $MIC_SOURCES; do
  pactl set-source-mute "$SOURCE" toggle
done
