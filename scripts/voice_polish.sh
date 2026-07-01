#!/usr/bin/env bash

# Light voice polish for WAV narration files.
#
# Usage:
#   scripts/voice_polish.sh
#   scripts/voice_polish.sh input.wav [output.wav]
#
# With no arguments, processes every *.wav file in the same directory as this
# script, writing *.polished.wav next to each source file. Files that already
# end in .polished.wav are skipped to avoid re-processing previous outputs.
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

filter_chain="
highpass=f=70,
equalizer=f=120:t=q:w=0.8:g=2.4,
equalizer=f=260:t=q:w=1.0:g=-0.8,
equalizer=f=3000:t=q:w=0.9:g=2.2,
equalizer=f=9000:t=q:w=0.7:g=2.0,
volume=9dB,
asoftclip=type=cubic:threshold=0.794:output=1.25:oversample=4
"

process_file() {
  local input_file="$1"
  local output_file="${2:-}"

  if [[ ! -f "$input_file" ]]; then
    echo "Input file does not exist: $input_file" >&2
    return 1
  fi

  if [[ -z "$output_file" ]]; then
    local input_dir
    local input_name
    local input_stem

    input_dir="$(dirname -- "$input_file")"
    input_name="$(basename -- "$input_file")"
    input_stem="${input_name%.*}"
    output_file="$input_dir/${input_stem}.polished.wav"
  fi

  if [[ "${output_file##*.}" != "wav" ]]; then
    echo "Output file must end with .wav" >&2
    return 1
  fi

  mkdir -p "$(dirname -- "$output_file")"

  ffmpeg -hide_banner -loglevel error -y \
    -i "$input_file" \
    -af "${filter_chain//$'\n'/}" \
    -ar 24000 \
    -ac 1 \
    -c:a pcm_s16le \
    -rf64 auto \
    "$output_file"

  echo "Generated $output_file"
}

if [[ $# -eq 0 ]]; then
  script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"

  shopt -s nullglob
  wav_files=("$script_dir"/*.wav)
  shopt -u nullglob

  if [[ ${#wav_files[@]} -eq 0 ]]; then
    echo "No .wav files found in $script_dir"
    exit 0
  fi

  processed=0

  for input_file in "${wav_files[@]}"; do
    if [[ "$input_file" == *.polished.wav ]]; then
      echo "Skipping already polished file: $input_file"
      continue
    fi

    process_file "$input_file"
    ((processed += 1))
  done

  if [[ $processed -eq 0 ]]; then
    echo "No source .wav files to process in $script_dir"
  fi

  exit 0
fi

if [[ $# -gt 2 ]]; then
  echo "Usage: $0 [input.wav [output.wav]]" >&2
  exit 1
fi

process_file "$1" "${2:-}"
