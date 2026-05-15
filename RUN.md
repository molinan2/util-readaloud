# Running

Activate the virtual environment:

```bash
source .venv/bin/activate
```

## Default Batch Mode

Convert every `.txt` and `.md` file in `files/in/` and write `.wav` files to
`files/out/`:

```bash
readaloud
```

## Single File

Convert one file next to the original:

```bash
readaloud notes.txt
```

Choose an explicit output path:

```bash
readaloud files/in/sample.txt -o files/out/sample.wav
```

## Directory

Convert every `.txt` and `.md` file directly inside a folder, writing each
`.wav` next to its source file:

```bash
readaloud files/in
```

## Options

CLI options override `config.toml`:

```bash
readaloud files/in/sample.md --lang e --voice ef_dora --speed 1.0
```

Current options:

```text
--lang   Kokoro language code
--voice  Kokoro voice name
--speed  Speech speed
-o       Output .wav path, only valid for a single input file
```

## Output

Normal runs print one line when a file starts and one line when it finishes:

```text
Processing files/in/sample.txt
Generated files/out/sample.wav (1 chunks, 2.7s)
Converted 1/1 files
```

Known noisy PyTorch/Kokoro/Hugging Face warnings are silenced by default.

Markdown files are read as plain text. No Markdown cleanup is applied.
