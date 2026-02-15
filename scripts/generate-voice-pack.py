"""Generate a peon-ping voice pack using Fish-Speech TTS voice cloning.

Requires Fish-Speech API server running at http://127.0.0.1:8080.

Usage:
    cd own-my-peon
    uv run python -X utf8 scripts/generate-voice-pack.py \
        --ref-audio path/to/reference.wav \
        --lines templates/lines_ja.json \
        --pack-name my_character --lang ja
"""

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

# Ensure project root is importable (for `voice` package)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ── Category-to-filename prefix mapping ──────────────────────────────
CATEGORY_PREFIXES = {
    "session.start": "SessionStart",
    "task.acknowledge": "TaskAck",
    "task.complete": "TaskDone",
    "task.error": "TaskError",
    "input.required": "InputReq",
    "resource.limit": "ResLimit",
    "user.spam": "UserSpam",
}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Generate a peon-ping voice pack via TTS voice cloning.",
    )
    p.add_argument("--ref-audio", type=Path, required=True,
                    help="Path to reference audio file (mp3/wav/flac)")
    p.add_argument("--lines", type=Path, required=True,
                    help="Path to lines JSON (category -> list of strings)")
    p.add_argument("--pack-name", required=True,
                    help="Pack name (used as folder name)")
    p.add_argument("--lang", default="ja", choices=["ja", "en", "ko"],
                    help="Language code (default: ja)")
    p.add_argument("--output-dir", type=Path, default=None,
                    help="Output dir (default: ~/.claude/hooks/peon-ping/packs/<pack-name>)")
    p.add_argument("--separate-vocals", action="store_true",
                    help="Run BGM separation on reference audio first")
    p.add_argument("--fish-speech-url", default=None,
                    help="Fish-Speech API URL (default: http://127.0.0.1:8080)")
    return p.parse_args()


def load_lines(path: Path) -> dict[str, list[str]]:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    for cat in data:
        if cat not in CATEGORY_PREFIXES:
            print(f"Warning: unknown category '{cat}', skipping")
    return {k: v for k, v in data.items() if k in CATEGORY_PREFIXES}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def build_manifest(pack_name: str, lang: str,
                   generated: dict[str, list[dict]]) -> dict:
    categories = {}
    for cat, sounds in generated.items():
        categories[cat] = {"sounds": sounds}
    return {
        "cesp_version": "1.0",
        "name": pack_name,
        "display_name": pack_name,
        "version": "1.0.0",
        "author": {"name": "voice-clone-generator"},
        "license": "personal-use",
        "language": lang,
        "categories": categories,
    }


def main():
    args = parse_args()

    # Resolve output directory
    if args.output_dir:
        pack_dir = args.output_dir
    else:
        packs_root = Path(os.path.expanduser(
            "~/.claude/hooks/peon-ping/packs"))
        pack_dir = packs_root / args.pack_name
    sounds_dir = pack_dir / "sounds"
    sounds_dir.mkdir(parents=True, exist_ok=True)

    # Validate reference audio
    ref_audio = args.ref_audio.resolve()
    if not ref_audio.exists():
        print(f"Error: reference audio not found: {ref_audio}")
        sys.exit(1)

    # Optional: separate vocals from BGM
    if args.separate_vocals:
        from voice.vocal_separator import separate_vocals
        print(f"[1/4] Separating vocals from {ref_audio}...")
        ref_audio = separate_vocals(ref_audio)
        print(f"  Cleaned audio: {ref_audio}")
    else:
        print(f"[1/4] Using reference audio as-is: {ref_audio}")

    # Load lines
    lines = load_lines(args.lines)
    if not lines:
        print("Error: no valid lines found in the JSON file")
        sys.exit(1)
    total = sum(len(v) for v in lines.values())
    print(f"[2/4] Loaded {total} lines across {len(lines)} categories")

    # Initialize TTS
    from voice.adapters.fish_speech import FishSpeechAdapter
    from voice.transcriber import Transcriber

    adapter = FishSpeechAdapter(api_url=args.fish_speech_url)
    if not adapter.is_available():
        print("Error: Fish-Speech API is not reachable at "
              f"{adapter.api_url}")
        print("  Start the server first. See docs/voice-clone-guide.md")
        sys.exit(1)

    # Transcribe reference for TTS conditioning
    transcriber = Transcriber(model_name="Qwen/Qwen3-ASR-0.6B")
    transcript_dir = PROJECT_ROOT / ".cache" / "transcripts"
    ref_text = transcriber.transcribe_with_cache(
        ref_audio, transcript_dir, language=args.lang,
    )
    print(f"  Reference transcript: {ref_text[:80]}...")

    # Generate voice lines
    print(f"[3/4] Generating {total} voice lines...")
    generated: dict[str, list[dict]] = {}
    count = 0
    for category, texts in lines.items():
        prefix = CATEGORY_PREFIXES[category]
        cat_sounds = []
        for i, text in enumerate(texts, 1):
            count += 1
            name = f"{prefix}{i}"
            out_path = sounds_dir / f"{name}.wav"

            if out_path.exists():
                print(f"  [{count}/{total}] Cached: {name}")
            else:
                print(f"  [{count}/{total}] Generating: {name} -> {text}")
                try:
                    adapter.generate(
                        text=text, lang=args.lang,
                        ref_audio=ref_audio, output_path=out_path,
                        ref_text=ref_text,
                    )
                except Exception as e:
                    print(f"    Error: {e}")
                    continue

            cat_sounds.append({
                "file": f"sounds/{name}.wav",
                "label": text,
                "sha256": sha256_file(out_path),
            })
        generated[category] = cat_sounds

    # Write manifest
    manifest = build_manifest(args.pack_name, args.lang, generated)
    manifest_path = pack_dir / "openpeon.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print(f"[4/4] Manifest written: {manifest_path}")

    print(f"\nDone! Pack '{args.pack_name}' -> {pack_dir}")
    print(f"  Activate: peon packs use {args.pack_name}")


if __name__ == "__main__":
    main()
