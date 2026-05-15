#!/usr/bin/env bash

# Light voice polish for WAV narration files.
#
# Usage:
#   scripts/voice_polish.sh input.wav [output.wav]
#
# If output.wav is omitted, writes input.polished.wav next to the source file.
#
# Processing chain:
#   - gentle high-pass filter
#   - narration-style EQ with extra body, presence, and brightness
#   - +9 dB gain into cubic soft clipping
#
# The soft clip starts around -2 dBFS and rounds peaks toward 0 dBFS. This is
# intentionally not dynamic compression: it is a static saturation/ceiling stage.
#
# This script is intentionally separate from readaloud: it is optional audio
# post-processing, not part of text-to-speech generation.

set -euo pipefail

if [[ $# -lt 1 || $# -gt 2 ]]; then
  echo "Usage: $0 input.wav [output.wav]"
  exit 1
fi

input_file="$1"
output_file="${2:-}"

if [[ ! -f "$input_file" ]]; then
  echo "Input file does not exist: $input_file"
  exit 1
fi

if [[ -z "$output_file" ]]; then
  input_dir="$(dirname "$input_file")"
  input_name="$(basename "$input_file")"
  input_stem="${input_name%.*}"
  output_file="$input_dir/${input_stem}.polished.wav"
fi

if [[ "${output_file##*.}" != "wav" ]]; then
  echo "Output file must end with .wav"
  exit 1
fi

mkdir -p "$(dirname "$output_file")"

filter_chain="
highpass=f=70,
equalizer=f=120:t=q:w=0.8:g=2.4,
equalizer=f=260:t=q:w=1.0:g=-0.8,
equalizer=f=3000:t=q:w=0.9:g=2.2,
equalizer=f=9000:t=q:w=0.7:g=2.0,
volume=9dB,
asoftclip=type=cubic:threshold=0.794:output=1.25:oversample=4
"

ffmpeg -hide_banner -loglevel error -y \
  -i "$input_file" \
  -af "${filter_chain//$'\n'/}" \
  -ar 24000 \
  -ac 1 \
  -c:a pcm_s16le \
  -rf64 auto \
  "$output_file"

echo "Generated $output_file"
