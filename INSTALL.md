# Installation

This project uses Python 3.12, Kokoro, and `soundfile` to generate WAV audio
from `.txt` and `.md` files.

## Requirements

- macOS with Homebrew
- `pyenv`
- Python 3.12
- `espeak-ng`

Kokoro currently requires Python `>=3.10,<3.14`, so Python 3.14 is not suitable
for this project.

## 1. Install pyenv

```bash
brew install pyenv
```

For `zsh`, add this to `~/.zshrc` if it is not already present:

```bash
export PYENV_ROOT="$HOME/.pyenv"
[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
```

Reload the shell:

```bash
exec "$SHELL"
```

## 2. Install Python

```bash
pyenv install 3.12
pyenv local 3.12
python --version
```

## 3. Install espeak-ng

```bash
brew install espeak-ng
espeak-ng --version
```

## 4. Create the virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

Verify:

```bash
which python
python --version
```

The Python path should point inside `.venv/`.

## 5. Install the project

Install dependencies and expose the `readaloud` command inside the active
virtual environment:

```bash
python -m pip install -r requirements.txt
python -m pip install -e .
```

Verify:

```bash
readaloud --help
```

## Notes

- `config.toml` stores default Kokoro settings and default input/output folders.
- CLI flags override `config.toml`.
- Markdown files are read as plain text.
- Known noisy PyTorch/Kokoro/Hugging Face warnings are silenced by default.
