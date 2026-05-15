# Installation Notes

This project builds a small Python command-line tool that reads `.txt` or `.md`
files and generates audio using Kokoro.

These notes track the setup decisions and commands as we go.

## Current Machine Context

- macOS on Apple Silicon (`arm64`)
- Homebrew is available
- `python3` currently points to Python 3.14.3
- `python` is not currently available in `PATH`
- `uv` is not currently available in `PATH`
- `pipx` is not currently available in `PATH`
- `espeak-ng` is not installed via Homebrew

## Python Version Choice

Kokoro currently declares:

```text
requires-python = ">=3.10, <3.14"
```

So Python 3.14 is not suitable for this project right now.

Recommended version for this project:

```text
Python 3.12.x
```

Python 3.11 would also be a conservative fallback if needed.

## Tools We Will Use

- `pyenv` to install and select the Python version for this project.
- `venv` to create a project-local virtual environment.
- `pip` to install Python packages inside that virtual environment.
- Homebrew to install system dependencies such as `espeak-ng`.

## Project Layout

Application code will live under:

```text
src/
```

Input and output files live under:

```text
files/in/
files/out/
```

## Step 1: Install pyenv

Install `pyenv` with Homebrew:

```bash
brew install pyenv
```

Then verify it is installed:

```bash
pyenv --version
```

## Step 2: Configure pyenv in the shell

For `zsh`, add this to `~/.zshrc` if it is not already present:

```bash
export PYENV_ROOT="$HOME/.pyenv"
[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
```

Then reload the shell:

```bash
exec "$SHELL"
```

Verify that `pyenv` works:

```bash
pyenv --version
```

## Step 3: Install Python 3.12

Install a Python 3.12 release with `pyenv`:

```bash
pyenv install 3.12
```

Set Python 3.12 for this project:

```bash
pyenv local 3.12
```

Verify:

```bash
python --version
```

## Step 4: Install espeak-ng

Kokoro uses `espeak-ng` for fallback and for some language support.

Install it with Homebrew:

```bash
brew install espeak-ng
```

Verify:

```bash
espeak-ng --version
```

## Step 5: Create the virtual environment

Create a project-local virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Verify that the active Python comes from `.venv`:

```bash
which python
python --version
```

Expected shape:

```text
/Users/juanma/dev/own/util-readaloud/.venv/bin/python
Python 3.12.x
```

## Step 6: Upgrade pip

With the virtual environment activated:

```bash
python -m pip install --upgrade pip
```

## Step 7: Install Python dependencies

Project dependencies are listed in:

```text
requirements.txt
```

Install them with the virtual environment activated:

```bash
python -m pip install -r requirements.txt
```

Verify that Kokoro can be imported:

```bash
python -c "import kokoro; print('kokoro ok')"
```

At this point, the import works.

## Next Step After This

Create a minimal smoke test under `src/` that generates a `.wav` file from a
fixed sentence.

Smoke test status:

- `src/smoke_kokoro.py` generates `smoke-0.wav`.
- The generated `.wav` has been listened to and works.

## Step 8: Read a text file

Create a simple script that reads a `.txt` or `.md` file and writes a `.wav`:

```bash
python src/read_aloud.py files/in/input.txt -o files/out/output.wav
```

Current behavior:

- Reads UTF-8 text from `.txt` or `.md`.
- Uses Spanish Kokoro settings: `lang_code="e"` and `voice="ef_dora"`.
- Writes a single `.wav` file at 24 kHz.
- Streams all generated chunks into one final audio file instead of keeping the
  full audio in memory.
- Uses RF64 output to support very large WAV-compatible files.
- If called without an input file, converts every `.txt` and `.md` file in
  `files/in/` and writes results to `files/out/`.

Optional CLI flags:

```bash
python src/read_aloud.py files/in/input.md -o files/out/output.wav --lang e --voice ef_dora --speed 1.0
```
