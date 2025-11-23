from pathlib import Path
import whisper
from typing import Any

DEFAULT_AUDIO_PATH = Path("./apps/audo_to_text/sample_files/first.wav")
DEFAULT_MODEL_NAME = "tiny"


class AudioFileTranscriber:
    """Transcriber for static audio files using a provided Whisper model.

    The model is supplied externally (e.g. by an application layer) to allow
    reuse across multiple transcriptions, centralized device placement, and
    future sharing with streaming pathways.
    """

    def __init__(self, audio_path: Path, model: Any):
        self.audio_path = audio_path
        self._model = model  # Preloaded whisper model instance

    @property
    def model(self):
        return self._model

    def load_and_prepare_audio(self):
        audio = whisper.load_audio(str(self.audio_path))
        audio = whisper.pad_or_trim(audio)
        mel = whisper.log_mel_spectrogram(audio).to(self.model.device)
        return audio, mel

    def detect_language(self, mel):
        _, probs = self.model.detect_language(mel)
        lang = max(probs, key=probs.get)
        return lang, probs

    def decode_audio(self, mel):
        options = whisper.DecodingOptions()
        result = whisper.decode(self.model, mel, options)
        return result.text

    def transcribe(self):
        _, mel = self.load_and_prepare_audio()
        lang, _ = self.detect_language(mel)
        text = self.decode_audio(mel)
        return lang, text
