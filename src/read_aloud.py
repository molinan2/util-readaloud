import argparse
from pathlib import Path

import soundfile as sf
from kokoro import KPipeline

SAMPLE_RATE = 24000
OUTPUT_FORMAT = "RF64"
DEFAULT_INPUT_DIR = Path("files/in")
DEFAULT_OUTPUT_DIR = Path("files/out")
INPUT_SUFFIXES = {".txt", ".md"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a WAV audio file from a .txt or .md file."
    )
    parser.add_argument(
        "input",
        nargs="?",
        type=Path,
        help="Input .txt or .md file. If omitted, all files in files/in/ are converted.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output .wav file. Required when input is provided.",
    )
    parser.add_argument(
        "--lang",
        default="e",
        help="Kokoro language code. Defaults to 'e' for Spanish.",
    )
    parser.add_argument(
        "--voice",
        default="ef_dora",
        help="Kokoro voice name. Defaults to 'ef_dora'.",
    )
    parser.add_argument(
        "--speed",
        type=float,
        default=1.0,
        help="Speech speed. Defaults to 1.0.",
    )
    return parser.parse_args()


def validate_paths(input_path: Path, output_path: Path) -> bool:
    if input_path.suffix.lower() not in {".txt", ".md"}:
        print(f"Skipping {input_path}: input file must be .txt or .md")
        return False

    if output_path.suffix.lower() != ".wav":
        print(f"Skipping {input_path}: output file must be .wav")
        return False

    return True


def convert_file(
    pipeline: KPipeline,
    input_path: Path,
    output_path: Path,
    voice: str,
    speed: float,
) -> bool:
    if not validate_paths(input_path, output_path):
        return False

    text = input_path.read_text(encoding="utf-8").strip()
    if not text:
        print(f"Skipping {input_path}: input file is empty")
        return False

    output_path.parent.mkdir(parents=True, exist_ok=True)
    generator = pipeline(text, voice=voice, speed=speed)

    chunks_written = 0
    frames_written = 0
    with sf.SoundFile(
        output_path,
        mode="w",
        samplerate=SAMPLE_RATE,
        channels=1,
        format=OUTPUT_FORMAT,
    ) as output_file:
        for _graphemes, _phonemes, audio in generator:
            output_file.write(audio)
            chunks_written += 1
            frames_written += len(audio)

    if chunks_written == 0:
        print(f"Skipping {input_path}: no audio was generated")
        return False

    seconds = frames_written / SAMPLE_RATE
    print(f"Generated {output_path} ({chunks_written} chunks, {seconds:.1f}s)")
    return True


def find_batch_inputs(input_dir: Path) -> list[Path]:
    if not input_dir.exists():
        return []

    return sorted(
        path
        for path in input_dir.iterdir()
        if path.is_file() and path.suffix.lower() in INPUT_SUFFIXES
    )


def main() -> int:
    args = parse_args()

    if args.input is not None and args.output is None:
        print("Output file is required when input is provided. Use -o output.wav")
        return 1

    if args.input is None and args.output is not None:
        print("Output file cannot be used in batch mode. Pass an input file too.")
        return 1

    pipeline = KPipeline(lang_code=args.lang, repo_id="hexgrad/Kokoro-82M")

    if args.input is not None:
        success = convert_file(
            pipeline=pipeline,
            input_path=args.input,
            output_path=args.output,
            voice=args.voice,
            speed=args.speed,
        )
        return 0 if success else 1

    input_paths = find_batch_inputs(DEFAULT_INPUT_DIR)
    if not input_paths:
        print(f"No .txt or .md files found in {DEFAULT_INPUT_DIR}/")
        return 1

    success_count = 0
    for input_path in input_paths:
        output_path = DEFAULT_OUTPUT_DIR / f"{input_path.stem}.wav"
        if convert_file(
            pipeline=pipeline,
            input_path=input_path,
            output_path=output_path,
            voice=args.voice,
            speed=args.speed,
        ):
            success_count += 1

    print(f"Converted {success_count}/{len(input_paths)} files")
    if success_count == 0:
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
