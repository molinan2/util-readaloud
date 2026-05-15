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
#   - subtle narration-style EQ for body, presence, and brightness
#   - about +6 dB input gain into moderate dynamic compression
#   - final limiter to avoid clipping
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
equalizer=f=130:t=q:w=0.8:g=1.5,
equalizer=f=320:t=q:w=1.0:g=-1.2,
equalizer=f=3200:t=q:w=0.9:g=1.6,
equalizer=f=8500:t=q:w=0.7:g=1.2,
acompressor=level_in=1.995:threshold=0.20:ratio=2.4:attack=12:release=180:makeup=1.15:knee=4:detection=rms,
alimiter=limit=0.97
"

ffmpeg -hide_banner -y \
  -i "$input_file" \
  -af "${filter_chain//$'\n'/}" \
  -ar 24000 \
  -ac 1 \
  -c:a pcm_s16le \
  -rf64 auto \
  "$output_file"

echo "Generated $output_file"
