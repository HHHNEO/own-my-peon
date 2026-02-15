"""Fish Speech adapter (local HTTP API server + HuggingFace model).

Requires:
  1. pip install fish-speech  (or clone repo + pip install -e .[cu129])
  2. Download model: hf download fishaudio/openaudio-s1-mini --local-dir checkpoints/openaudio-s1-mini
  3. Start API server before running:
     python -m tools.api_server \
       --listen 127.0.0.1:8080 \
       --llama-checkpoint-path checkpoints/openaudio-s1-mini \
       --decoder-checkpoint-path checkpoints/openaudio-s1-mini/codec.pth \
       --decoder-config-name modded_dac_vq --compile
"""

import os
from pathlib import Path
from typing import Optional

import msgpack
import requests

from .base import TTSAdapter

DEFAULT_API_URL = "http://127.0.0.1:8080"


class FishSpeechAdapter(TTSAdapter):
    name = "fish-speech"
    supports_voice_clone = True
    supported_languages = ["ja", "en", "ko"]

    def __init__(self, api_url: str | None = None):
        self.api_url = api_url or os.environ.get(
            "FISH_SPEECH_API_URL", DEFAULT_API_URL,
        )

    def is_available(self) -> bool:
        try:
            r = requests.get(f"{self.api_url}/v1/health", timeout=3)
            return r.status_code == 200
        except (requests.ConnectionError, requests.Timeout):
            return False

    def generate(
        self,
        text: str,
        lang: str,
        ref_audio: Path,
        output_path: Path,
        ref_text: Optional[str] = None,
    ) -> Path:
        ref_bytes = ref_audio.read_bytes()

        payload = {
            "text": text,
            "references": [
                {"audio": ref_bytes, "text": ref_text or ""},
            ],
            "format": "wav",
            "streaming": False,
        }

        resp = requests.post(
            f"{self.api_url}/v1/tts",
            data=msgpack.packb(payload),
            headers={"Content-Type": "application/msgpack"},
            timeout=300,
        )
        resp.raise_for_status()

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(resp.content)
        return output_path

    def install_hint(self) -> str:
        return (
            "pip install fish-speech  (or: git clone + pip install -e .[cu129])\n"
            "  hf download fishaudio/openaudio-s1-mini "
            "--local-dir checkpoints/openaudio-s1-mini\n"
            "  Then start the API server:\n"
            "  python -m tools.api_server --listen 127.0.0.1:8080 \\\n"
            "    --llama-checkpoint-path checkpoints/openaudio-s1-mini \\\n"
            "    --decoder-checkpoint-path checkpoints/openaudio-s1-mini/codec.pth \\\n"
            "    --decoder-config-name modded_dac_vq --compile"
        )
