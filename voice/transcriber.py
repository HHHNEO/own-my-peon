"""Auto-transcription using Qwen3-ASR."""

from pathlib import Path
from typing import Optional

# Qwen3-ASR expects full language names, not ISO codes.
ASR_LANG_MAP = {
    "ja": "Japanese",
    "en": "English",
    "ko": "Korean",
}


class Transcriber:
    """Speech-to-text transcriber using Qwen3-ASR."""

    def __init__(self, model_name: str = "Qwen/Qwen3-ASR-0.6B"):
        self.model_name = model_name
        self._model = None

    def _load_model(self):
        if self._model is not None:
            return
        import torch
        from qwen_asr import Qwen3ASRModel

        device = "cuda:0" if torch.cuda.is_available() else "cpu"
        dtype = torch.bfloat16 if torch.cuda.is_available() else torch.float32
        print(f"  Loading ASR model {self.model_name} on {device}...")
        self._model = Qwen3ASRModel.from_pretrained(
            self.model_name,
            device_map=device,
            dtype=dtype,
        )

    def transcribe(self, audio_path: Path, language: Optional[str] = None) -> str:
        """Transcribe audio file to text."""
        self._load_model()
        asr_language = ASR_LANG_MAP.get(language, language) if language else None
        results = self._model.transcribe(
            audio=str(audio_path),
            language=asr_language,
        )
        if results and len(results) > 0:
            return results[0].text
        return ""

    def transcribe_with_cache(
        self,
        audio_path: Path,
        transcript_dir: Path,
        language: Optional[str] = None,
    ) -> str:
        """Transcribe audio, caching result to a text file."""
        lang_dir = transcript_dir / language if language else transcript_dir
        cache_path = lang_dir / f"{audio_path.stem}.txt"

        if cache_path.exists():
            text = cache_path.read_text(encoding="utf-8").strip()
            if text:
                print(f"[ASR] Cached transcript: {cache_path}")
                return text

        text = self.transcribe(audio_path, language=language)

        lang_dir.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(text, encoding="utf-8")
        print(f"[ASR] Saved transcript: {cache_path}")
        return text
