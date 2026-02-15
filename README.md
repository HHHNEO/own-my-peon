# own-my-peon

Fork of [PeonPing/peon-ping](https://github.com/PeonPing/peon-ping) — **TTS voice cloning으로 나만의 peon-ping 음성팩 만들기**.

peon-ping은 AI 코딩 에이전트가 알림을 줄 때 게임 캐릭터 음성을 재생합니다. 이 fork는 좋아하는 캐릭터의 음성을 클로닝해서 나만의 음성팩을 만드는 도구와 가이드를 제공합니다.

---

## What this fork adds

| | Description |
|---|---|
| **[Voice Clone Guide](docs/voice-clone-guide.md)** | 레퍼런스 오디오 하나로 음성팩 생성하는 전체 가이드 (한/영) |
| **[generate-voice-pack.py](scripts/generate-voice-pack.py)** | Fish-Speech TTS + BGM 분리 + openpeon.json 자동 생성 스크립트 |
| **[Line templates](templates/)** | 일본어/영어 대사 템플릿 (CESP 카테고리별) |

## Quick start

### 1. Install peon-ping

원본 peon-ping을 먼저 설치합니다:

```bash
# macOS / Linux
curl -fsSL https://raw.githubusercontent.com/PeonPing/peon-ping/main/install.sh | bash

# Windows
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/PeonPing/peon-ping/main/install.ps1" -UseBasicParsing | Invoke-Expression
```

> 전체 설치 옵션과 설정 방법: [PeonPing/peon-ping README](https://github.com/PeonPing/peon-ping)

### 2. Clone this repo & install dependencies

```bash
git clone https://github.com/HHHNEO/own-my-peon.git
cd own-my-peon
uv sync
```

### 3. Set up Fish-Speech TTS

```bash
# Download TTS model (first time only)
huggingface-cli download fishaudio/openaudio-s1-mini --local-dir checkpoints/openaudio-s1-mini

# Start API server (keep running in background)
uv run python -m tools.api_server \
  --listen 127.0.0.1:8080 \
  --llama-checkpoint-path checkpoints/openaudio-s1-mini \
  --decoder-checkpoint-path checkpoints/openaudio-s1-mini/codec.pth \
  --decoder-config-name modded_dac_vq --compile
```

### 4. Generate your voice pack

```bash
# In another terminal
uv run python -X utf8 scripts/generate-voice-pack.py \
  --ref-audio path/to/character_voice.wav \
  --lines templates/lines_ja.json \
  --pack-name my_character \
  --lang ja

# Activate
peon packs use my_character
```

**[Full guide with all options &rarr; docs/voice-clone-guide.md](docs/voice-clone-guide.md)**

## Requirements

| Tool | Purpose |
|------|---------|
| [peon-ping](https://github.com/PeonPing/peon-ping) | Sound notification system |
| Python 3.10+ | Runtime |
| [uv](https://docs.astral.sh/uv/) | Python package manager |
| ffmpeg | Audio processing |
| NVIDIA GPU (recommended) | Fish-Speech TTS inference |

## Line templates

대사를 커스터마이징하려면 `templates/` 폴더의 JSON을 복사해서 수정하세요:

- [`templates/lines_ja.json`](templates/lines_ja.json) — 일본어 (Japanese)
- [`templates/lines_en.json`](templates/lines_en.json) — 영어 (English)

각 [CESP 카테고리](https://github.com/PeonPing/openpeon)별로 대사를 정의합니다:

```json
{
  "session.start": ["Hello!", "Ready to go!"],
  "task.complete": ["Done!", "All finished!"],
  "input.required": ["Need your input!"],
  ...
}
```

## Upstream

이 fork는 [PeonPing/peon-ping](https://github.com/PeonPing/peon-ping)의 fork입니다. peon-ping 자체의 설치, 설정, IDE 지원, 사운드팩 목록 등은 원본 README를 참조하세요.

## License

[MIT](LICENSE)
