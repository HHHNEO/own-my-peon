"""Standalone vocal separation script — runs in its own venv (tools/.venv).

Usage:
    python tools/separate_vocals.py <input_path> <output_dir> [--model MODEL]

Outputs the vocal wav path to stdout (last line).
"""

import argparse
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Separate vocals from BGM")
    parser.add_argument("input_path", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument(
        "--model",
        default="model_bs_roformer_ep_317_sdr_12.9755.ckpt",
        help="Model filename for audio-separator",
    )
    args = parser.parse_args()

    if not args.input_path.exists():
        print(f"Error: {args.input_path} not found", file=sys.stderr)
        sys.exit(1)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    cleaned_path = args.output_dir / f"{args.input_path.stem}.wav"

    # Skip if already separated
    if cleaned_path.exists():
        print(f"[Vocal] Using cached: {cleaned_path}", file=sys.stderr)
        print(cleaned_path)
        return

    from audio_separator.separator import Separator

    print(f"[Vocal] Separating vocals from: {args.input_path}", file=sys.stderr)
    separator = Separator(
        output_dir=str(args.output_dir),
        output_format="wav",
    )
    separator.load_model(model_filename=args.model)
    output_files = separator.separate(str(args.input_path))

    resolved = []
    for f in output_files:
        p = Path(f)
        if not p.exists():
            p = args.output_dir / p.name
        resolved.append(p)

    vocal_file = None
    for p in resolved:
        if "vocal" in p.stem.lower():
            vocal_file = p
            break
    if vocal_file is None and resolved:
        vocal_file = resolved[0]
    if vocal_file is None:
        print("Error: No output files from separation", file=sys.stderr)
        sys.exit(1)

    if vocal_file.resolve() != cleaned_path.resolve():
        vocal_file.rename(cleaned_path)

    for p in resolved:
        if p.exists() and p.resolve() != cleaned_path.resolve():
            p.unlink()

    print(f"[Vocal] Saved: {cleaned_path}", file=sys.stderr)
    print(cleaned_path)


if __name__ == "__main__":
    main()
