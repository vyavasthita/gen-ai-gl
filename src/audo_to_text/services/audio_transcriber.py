from pathlib import Path
import whisper
from .model_loader import ModelLoader

DEFAULT_AUDIO_PATH = Path("./src/audo_to_text/sample_files/first.wav")
DEFAULT_MODEL_NAME = "tiny"

class AudioFileTranscriber:
    """Transcriber for static audio files.

    Handles end-to-end: file loading, spectrogram creation, language detection,
    and decoding. Focused on batch/offline usage.
    """

    def __init__(self, audio_path: Path = DEFAULT_AUDIO_PATH, model_name: str = DEFAULT_MODEL_NAME):
        self.audio_path = audio_path
        self.model_name = model_name
        self._loader = ModelLoader(model_name)
        self._model = None  # Lazy-loaded whisper model

    @property
    def model(self):
        if self._model is None:
            self._model = self._loader.load()
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
