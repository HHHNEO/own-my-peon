"""Vocal separation — delegates to tools/separate_vocals.py in its own venv.

audio-separator has dependency conflicts with fish-speech (protobuf, numpy),
so it runs in an isolated venv at tools/.venv.
"""

import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TOOLS_DIR = PROJECT_ROOT / "tools"
TOOLS_VENV_PYTHON = TOOLS_DIR / ".venv" / (
    "Scripts/python.exe" if sys.platform == "win32" else "bin/python"
)
SEPARATOR_SCRIPT = TOOLS_DIR / "separate_vocals.py"
FFMPEG_DIR = TOOLS_DIR / "ffmpeg" / "ffmpeg-master-latest-win64-gpl" / "bin"


def _ensure_tools_venv():
    """Create tools/.venv and install audio-separator if not present."""
    if TOOLS_VENV_PYTHON.exists():
        return
    print("[Vocal] Setting up tools venv (first run)...")
    subprocess.check_call(
        [sys.executable, "-m", "uv", "venv", str(TOOLS_DIR / ".venv")],
        cwd=str(TOOLS_DIR),
    )
    subprocess.check_call(
        [sys.executable, "-m", "uv", "pip", "install",
         "audio-separator[cpu]", "--python", str(TOOLS_VENV_PYTHON)],
    )
    print("[Vocal] Tools venv ready.")


def separate_vocals(input_path: Path, output_dir: Path | None = None) -> Path:
    """Separate vocals from BGM via subprocess, return cleaned vocal path."""
    if output_dir is None:
        output_dir = PROJECT_ROOT / "01_cleaned"

    # Fast path: cache check without spawning subprocess
    cleaned_path = output_dir / f"{input_path.stem}.wav"
    if cleaned_path.exists():
        print(f"[Vocal] Using cached: {cleaned_path}")
        return cleaned_path

    _ensure_tools_venv()

    # Ensure ffmpeg is on PATH for the subprocess
    env = os.environ.copy()
    if FFMPEG_DIR.exists():
        env["PATH"] = str(FFMPEG_DIR) + os.pathsep + env.get("PATH", "")

    result = subprocess.run(
        [str(TOOLS_VENV_PYTHON), str(SEPARATOR_SCRIPT),
         str(input_path), str(output_dir)],
        capture_output=True, text=True, env=env,
    )

    if result.stderr:
        for line in result.stderr.strip().splitlines():
            print(line)

    if result.returncode != 0:
        raise RuntimeError(
            f"Vocal separation failed (exit {result.returncode}): {result.stderr}"
        )

    out_path = Path(result.stdout.strip().splitlines()[-1])
    if not out_path.exists():
        raise RuntimeError(f"Expected output not found: {out_path}")

    return out_path
