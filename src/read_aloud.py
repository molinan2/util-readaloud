import argparse
import logging
import os
import tomllib
import warnings
from pathlib import Path

import soundfile as sf
from kokoro import KPipeline

SAMPLE_RATE = 24000
OUTPUT_FORMAT = "RF64"
DEFAULT_CONFIG_PATH = Path("config.toml")
DEFAULT_REPO_ID = "hexgrad/Kokoro-82M"
DEFAULT_LANG = "e"
DEFAULT_VOICE = "em_alex"
DEFAULT_SPEED = 0.9
DEFAULT_INPUT_DIR = Path("files/in")
DEFAULT_OUTPUT_DIR = Path("files/out")
INPUT_SUFFIXES = {".txt", ".md"}


def configure_library_noise() -> None:
    os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")
    logging.getLogger("huggingface_hub").setLevel(logging.ERROR)
    warnings.filterwarnings(
        "ignore",
        message="dropout option adds dropout after all but last recurrent layer.*",
        category=UserWarning,
        module="torch.nn.modules.rnn",
    )
    warnings.filterwarnings(
        "ignore",
        message="`torch.nn.utils.weight_norm` is deprecated.*",
        category=FutureWarning,
        module="torch.nn.utils.weight_norm",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a WAV audio file from a .txt or .md file."
    )
    parser.add_argument(
        "input",
        nargs="?",
        type=Path,
        help=(
            "Input .txt/.md file or directory. Files become .wav next to the "
            "input by default. Directories convert all .txt/.md files inside."
        ),
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output .wav file. Only valid when input is a single file.",
    )
    parser.add_argument(
        "-l",
        "--lang",
        help="Kokoro language code. Overrides config.toml.",
    )
    parser.add_argument(
        "-v",
        "--voice",
        help="Kokoro voice name. Overrides config.toml.",
    )
    parser.add_argument(
        "-s",
        "--speed",
        type=float,
        help="Speech speed. Overrides config.toml.",
    )
    return parser.parse_args()


def load_config(config_path: Path = DEFAULT_CONFIG_PATH) -> dict:
    config = {
        "repo_id": DEFAULT_REPO_ID,
        "lang": DEFAULT_LANG,
        "voice": DEFAULT_VOICE,
        "speed": DEFAULT_SPEED,
        "input_dir": DEFAULT_INPUT_DIR,
        "output_dir": DEFAULT_OUTPUT_DIR,
    }

    if not config_path.is_file():
        return config

    with config_path.open("rb") as config_file:
        parsed = tomllib.load(config_file)

    kokoro_config = parsed.get("kokoro", {})
    paths_config = parsed.get("paths", {})

    config["repo_id"] = kokoro_config.get("repo_id", config["repo_id"])
    config["lang"] = kokoro_config.get("lang", config["lang"])
    config["voice"] = kokoro_config.get("voice", config["voice"])
    config["speed"] = float(kokoro_config.get("speed", config["speed"]))
    config["input_dir"] = Path(paths_config.get("input_dir", config["input_dir"]))
    config["output_dir"] = Path(paths_config.get("output_dir", config["output_dir"]))

    return config


def validate_paths(input_path: Path, output_path: Path) -> bool:
    if not input_path.is_file():
        print(f"Skipping {input_path}: input file does not exist")
        return False

    if input_path.suffix.lower() not in {".txt", ".md"}:
        print(f"Skipping {input_path}: input file must be .txt or .md")
        return False

    if output_path.suffix.lower() != ".wav":
        print(f"Skipping {input_path}: output file must be .wav")
        return False

    return True


def default_output_path(input_path: Path, output_dir: Path | None = None) -> Path:
    parent = output_dir if output_dir is not None else input_path.parent
    return parent / f"{input_path.stem}.wav"


def convert_file(
    pipeline: KPipeline,
    input_path: Path,
    output_path: Path,
    voice: str,
    speed: float,
) -> bool:
    if not validate_paths(input_path, output_path):
        return False

    print(f"Processing {input_path}")
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


def convert_many(
    pipeline: KPipeline,
    input_paths: list[Path],
    voice: str,
    speed: float,
    output_dir: Path | None = None,
) -> int:
    if not input_paths:
        print("No .txt or .md files found")
        return 1

    success_count = 0
    for input_path in input_paths:
        output_path = default_output_path(input_path, output_dir=output_dir)
        if convert_file(
            pipeline=pipeline,
            input_path=input_path,
            output_path=output_path,
            voice=voice,
            speed=speed,
        ):
            success_count += 1

    print(f"Converted {success_count}/{len(input_paths)} files")
    return 0 if success_count > 0 else 1


def main() -> int:
    configure_library_noise()
    args = parse_args()
    config = load_config()

    lang = args.lang or config["lang"]
    voice = args.voice or config["voice"]
    speed = args.speed if args.speed is not None else config["speed"]

    if args.input is None and args.output is not None:
        print(
            "Output file cannot be used in default batch mode. Pass an input file too."
        )
        return 1

    if args.input is None:
        input_dir = config["input_dir"]
        output_dir = config["output_dir"]
        input_paths = find_batch_inputs(input_dir)
        if not input_paths:
            print(f"No .txt or .md files found in {input_dir}/")
            return 1
        pipeline = KPipeline(lang_code=lang, repo_id=config["repo_id"])
        return convert_many(
            pipeline=pipeline,
            input_paths=input_paths,
            voice=voice,
            speed=speed,
            output_dir=output_dir,
        )

    if args.input.is_dir():
        if args.output is not None:
            print("Output file cannot be used when input is a directory.")
            return 1

        input_paths = find_batch_inputs(args.input)
        if not input_paths:
            print(f"No .txt or .md files found in {args.input}/")
            return 1
        pipeline = KPipeline(lang_code=lang, repo_id=config["repo_id"])
        return convert_many(
            pipeline=pipeline,
            input_paths=input_paths,
            voice=voice,
            speed=speed,
        )

    output_path = args.output or default_output_path(args.input)
    if not validate_paths(args.input, output_path):
        return 1

    pipeline = KPipeline(lang_code=lang, repo_id=config["repo_id"])
    success = convert_file(
        pipeline=pipeline,
        input_path=args.input,
        output_path=output_path,
        voice=voice,
        speed=speed,
    )
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
