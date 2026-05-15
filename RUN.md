# Running

Activate the virtual environment first:

```bash
source .venv/bin/activate
```

## Batch mode

Convert every `.txt` and `.md` file in `files/in/` and write `.wav` files to
`files/out/`:

```bash
python src/read_aloud.py
```

## Single file mode

Convert one explicit file:

```bash
python src/read_aloud.py files/in/sample.txt -o files/out/sample.wav
```

Optional settings:

```bash
python src/read_aloud.py files/in/sample.md -o files/out/sample.wav --lang e --voice ef_dora --speed 1.0
```
