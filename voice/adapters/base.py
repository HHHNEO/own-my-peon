"""Base adapter interface for TTS models."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional


class TTSAdapter(ABC):
    """Voice cloning TTS adapter base class."""

    name: str = "base"
    supports_voice_clone: bool = False
    supported_languages: list[str] = []

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the model/package is installed and ready."""
        ...

    @abstractmethod
    def generate(
        self,
        text: str,
        lang: str,
        ref_audio: Path,
        output_path: Path,
        ref_text: Optional[str] = None,
    ) -> Path:
        """Generate TTS audio with voice cloning.

        Args:
            text: Text to synthesize.
            lang: Language code ('ja', 'en', 'ko').
            ref_audio: Path to reference voice audio file.
            output_path: Path to save the generated audio.
            ref_text: Optional transcript of the reference audio.

        Returns:
            Path to the generated audio file.
        """
        ...

    def install_hint(self) -> str:
        """Return installation instructions."""
        return f"Install {self.name} to use this adapter."
