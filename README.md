# own-my-peon

Fork of [PeonPing/peon-ping](https://github.com/PeonPing/peon-ping) — **Create your own peon-ping voice pack with TTS voice cloning.**

peon-ping plays game character voice lines when your AI coding agent needs attention. This fork provides tools and a guide for cloning any character's voice to build your own custom voice pack.

---

## What this fork adds

| | Description |
|---|---|
| **[Voice Clone Guide](docs/voice-clone-guide.md)** | End-to-end guide for generating a voice pack from a single reference audio clip |
| **[generate-voice-pack.py](scripts/generate-voice-pack.py)** | Automation script — Fish-Speech TTS + BGM separation + openpeon.json generation |
| **[Line templates](templates/)** | Ready-made dialogue templates for Japanese and English (per CESP category) |

## Quick start

### 1. Install peon-ping

Install the upstream peon-ping first:

```bash
# macOS / Linux
curl -fsSL https://raw.githubusercontent.com/PeonPing/peon-ping/main/install.sh | bash

# Windows (PowerShell)
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/PeonPing/peon-ping/main/install.ps1" -UseBasicParsing | Invoke-Expression
```

> For all install options and configuration, see the [PeonPing/peon-ping README](https://github.com/PeonPing/peon-ping).

### 2. Clone this repo & install dependencies

```bash
git clone https://github.com/HHHNEO/own-my-peon.git
cd own-my-peon
uv sync
```

### 3. Set up Fish-Speech TTS server

The generator script calls the [Fish-Speech](https://github.com/fishaudio/fish-speech) HTTP API. You need to install and run the server **separately**.

```bash
# Install Fish-Speech in a separate directory
git clone https://github.com/fishaudio/fish-speech.git
cd fish-speech
pip install -e .

# Download the model (first time only)
huggingface-cli download fishaudio/openaudio-s1-mini --local-dir checkpoints/openaudio-s1-mini

# Start the API server (keep running in background)
python -m tools.api_server \
  --listen 127.0.0.1:8080 \
  --llama-checkpoint-path checkpoints/openaudio-s1-mini \
  --decoder-checkpoint-path checkpoints/openaudio-s1-mini/codec.pth \
  --decoder-config-name modded_dac_vq --compile
```

> **Note**: A CUDA GPU is required for Fish-Speech inference. See the [Fish-Speech docs](https://speech.fish.audio/) for detailed setup instructions. The server is ready when `http://127.0.0.1:8080` responds.

### 4. Generate your voice pack

```bash
# From the own-my-peon directory (in another terminal)
uv run python -X utf8 scripts/generate-voice-pack.py \
  --ref-audio path/to/character_voice.wav \
  --lines templates/lines_ja.json \
  --pack-name my_character \
  --lang ja

# Activate the generated pack
peon packs use my_character
```

What the script does:
1. Auto-transcribes the reference audio via ASR (Qwen3-ASR)
2. Generates each line with Fish-Speech TTS voice cloning
3. Builds an `openpeon.json` manifest with SHA-256 checksums
4. Outputs directly to the peon-ping packs directory

**[Full options and detailed guide &rarr; docs/voice-clone-guide.md](docs/voice-clone-guide.md)**

## Requirements

| Tool | Purpose |
|------|---------|
| [peon-ping](https://github.com/PeonPing/peon-ping) | Sound notification system |
| Python 3.10+ | Runtime |
| [uv](https://docs.astral.sh/uv/) | Python package manager |
| [Fish-Speech](https://github.com/fishaudio/fish-speech) | TTS server (separate install) |
| NVIDIA GPU | Required for Fish-Speech inference |

## Line templates

Copy and edit the JSON templates in `templates/` to customize your lines:

- [`templates/lines_ja.json`](templates/lines_ja.json) — Japanese
- [`templates/lines_en.json`](templates/lines_en.json) — English

Define lines for each [CESP category](https://github.com/PeonPing/openpeon):

```json
{
  "session.start": ["Hello!", "Ready to go!"],
  "task.acknowledge": ["Got it!", "On it!"],
  "task.complete": ["Done!", "All finished!"],
  "task.error": ["Oops...", "Something broke..."],
  "input.required": ["Need your input!"],
  "resource.limit": ["I'm tired..."],
  "user.spam": ["Slow down!"]
}
```

## Upstream

This is a fork of [PeonPing/peon-ping](https://github.com/PeonPing/peon-ping). For peon-ping installation, configuration, IDE support, and the full sound pack catalog, see the upstream README.

## License

[MIT](LICENSE)
