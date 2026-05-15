# util-readaloud

Small Python CLI that reads `.txt` and `.md` files and generates `.wav` audio
with [Kokoro](https://github.com/hexgrad/kokoro).

## Quick Start

Set up the project first:

```bash
source .venv/bin/activate
python -m pip install -e .
```

Then run:

```bash
readaloud
```

By default, this converts every `.txt` and `.md` file in `files/in/` and writes
the generated `.wav` files to `files/out/`.

## Common Commands

Convert one file next to the original:

```bash
readaloud notes.txt
```

Convert one folder next to the source files:

```bash
readaloud path/to/folder
```

Choose an explicit output path:

```bash
readaloud files/in/sample.txt -o files/out/sample.wav
```

## Configuration

Defaults live in `config.toml`:

```toml
[kokoro]
repo_id = "hexgrad/Kokoro-82M"
lang = "e"
voice = "ef_dora"
speed = 1.0

[paths]
input_dir = "files/in"
output_dir = "files/out"
```

CLI flags override the config:

```bash
readaloud notes.md --voice ef_dora --speed 1.0
```

Markdown files are read as plain text.

## Docs

- Setup: `INSTALL.md`
- Usage: `RUN.md`
