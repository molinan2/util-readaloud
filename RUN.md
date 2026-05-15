# Running

Activate the virtual environment first:

```bash
source .venv/bin/activate
```

## Batch mode

Convert every `.txt` and `.md` file in `files/in/` and write `.wav` files to
`files/out/`:

```bash
readaloud
```

## Single file mode

Convert one explicit file next to the original, with the same base name:

```bash
readaloud notes.txt
```

Or choose the output path explicitly:

```bash
readaloud files/in/sample.txt -o files/out/sample.wav
```

## Directory mode

Convert every `.txt` and `.md` file directly inside a folder, writing each
`.wav` next to its source file:

```bash
readaloud files/in
```

## Optional settings

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
readaloud files/in/sample.md --lang e --voice ef_dora --speed 1.0
```

Markdown files are read as plain text. No Markdown cleanup is applied.

## Global command

Install the project in editable mode inside the virtual environment:

```bash
python -m pip install -e .
```

Then run:

```bash
readaloud
readaloud notes.txt
readaloud files/in
```

The underlying script can still be run directly:

```bash
python src/read_aloud.py
```

Known noisy library warnings from PyTorch/Kokoro/Hugging Face are silenced by
default so normal runs only print conversion progress.
