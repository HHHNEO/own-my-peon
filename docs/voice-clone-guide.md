# Create Your Own Voice Pack with TTS Voice Cloning

peon-ping ships with game character voice packs, but you can create a pack with **any voice** using TTS voice cloning. This guide walks you through generating a custom voice pack from a single reference audio clip.

**TTS 음성 클로닝으로 나만의 음성팩 만들기** — 레퍼런스 오디오 하나로 좋아하는 캐릭터의 peon-ping 음성팩을 생성할 수 있습니다.

---

## Prerequisites / 사전 준비

| Tool | Purpose |
|------|---------|
| Python 3.10+ | Runtime |
| [uv](https://docs.astral.sh/uv/) | Python package manager |
| [Fish-Speech](https://github.com/fishaudio/fish-speech) | TTS server (별도 설치 필요) |
| NVIDIA GPU | Fish-Speech 추론용 (필수) |
| ffmpeg | Audio processing (`--separate-vocals` 사용 시) |

## Step 1: Prepare Reference Audio / 레퍼런스 음성 준비

Collect a short (5-30 second) audio clip of the target voice. Supported formats: `.mp3`, `.wav`, `.flac`.

- BGM이 섞여 있어도 괜찮습니다 — 스크립트가 자동으로 보컬을 분리합니다 (`--separate-vocals`).
- 대사가 명확하게 들리는 클립일수록 결과가 좋습니다.

## Step 2: Clone & Install / 프로젝트 설치

```bash
git clone https://github.com/HHHNEO/own-my-peon.git
cd own-my-peon
uv sync
```

### Start the Fish-Speech API server

Fish-Speech는 own-my-peon과 **별도로** 설치해야 합니다:

```bash
# 별도 디렉토리에서 Fish-Speech 설치
git clone https://github.com/fishaudio/fish-speech.git
cd fish-speech
pip install -e .

# 모델 다운로드 (최초 1회)
huggingface-cli download fishaudio/openaudio-s1-mini --local-dir checkpoints/openaudio-s1-mini

# API 서버 시작 (백그라운드로 유지)
python -m tools.api_server \
  --listen 127.0.0.1:8080 \
  --llama-checkpoint-path checkpoints/openaudio-s1-mini \
  --decoder-checkpoint-path checkpoints/openaudio-s1-mini/codec.pth \
  --decoder-config-name modded_dac_vq --compile
```

> 자세한 설치 방법은 [Fish-Speech 공식 문서](https://speech.fish.audio/)를 참고하세요.

서버가 `http://127.0.0.1:8080`에서 응답하면 준비 완료입니다. 확인:

```bash
curl http://127.0.0.1:8080/v1/health
# {"status":"ok"}
```

## Step 3: Define Lines & Generate / 대사 정의 & 음성 생성

### Using a template

The `templates/` folder has ready-made line files:

- `templates/lines_ja.json` — Japanese lines (日本語)
- `templates/lines_en.json` — English lines

### Customize your lines

Copy a template and edit it. Each CESP category needs at least one line:

```json
{
  "session.start": ["Hello!", "Ready to go!"],
  "task.acknowledge": ["Got it!", "On it!"],
  "task.complete": ["Done!", "All finished!"],
  "task.error": ["Oops...", "Something broke..."],
  "input.required": ["Need your input!", "Hey, you there?"],
  "resource.limit": ["I'm tired...", "Need a break..."],
  "user.spam": ["Slow down!", "Too fast!"]
}
```

### Run the generator

```bash
uv run python -X utf8 scripts/generate-voice-pack.py \
  --ref-audio path/to/character_voice.wav \
  --lines templates/lines_ja.json \
  --pack-name my_character \
  --lang ja
```

**Options:**

| Flag | Description | Default |
|------|-------------|---------|
| `--ref-audio` | Path to reference audio file | (required) |
| `--lines` | Path to lines JSON file | (required) |
| `--pack-name` | Name for the generated pack | (required) |
| `--lang` | Language code (`ja`, `en`, `ko`) | `ja` |
| `--output-dir` | Output directory | `~/.claude/hooks/peon-ping/packs/<pack-name>` |
| `--separate-vocals` | Run BGM separation on reference audio | `false` |
| `--fish-speech-url` | Fish-Speech API URL | `http://127.0.0.1:8080` |

The script will:

1. (Optional) Separate vocals from BGM using audio-separator
2. Transcribe the reference audio with Qwen3-ASR
3. Generate each line via Fish-Speech TTS
4. Build `openpeon.json` manifest with SHA-256 checksums
5. Output a complete pack ready for peon-ping

## Step 4: Install the Pack / 팩 설치

The generator outputs directly to the peon-ping packs directory by default. Activate it:

```bash
peon packs use my_character
```

Or copy manually:

```bash
# The generated pack folder structure:
# my_character/
#   openpeon.json
#   sounds/
#     SessionStart1.wav
#     SessionStart2.wav
#     ...

cp -r my_character ~/.claude/hooks/peon-ping/packs/
peon packs use my_character
```

## Tips / 팁

- **Better reference = better clone**: Clean dialogue without background noise produces the best results.
- **BGM separation**: Use `--separate-vocals` if your reference has background music. The script uses [audio-separator](https://github.com/nomadkaraoke/python-audio-separator) to extract vocals.
- **Multiple references**: For best quality, use a reference clip where the speaker's tone matches the style you want (e.g. cheerful for greetings, surprised for errors).
- **Iterating**: Generated files are cached — delete a specific `.wav` from `sounds/` to regenerate just that line.
