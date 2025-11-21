from pathlib import Path
import whisper
from .model_loader import ModelLoader

DEFAULT_AUDIO_PATH = Path("./src/audo_to_text/sample_files/first.wav")
DEFAULT_MODEL_NAME = "tiny"

class Transcriber:
    """High-level transcription orchestrator for a single audio file.

    Encapsulates steps: load model, load/prepare audio, language detection,
    decoding. Designed for easy extension (batching, alternative decoding
    options, error handling) while keeping current flow minimal.
    """

    def __init__(self, audio_path: Path = DEFAULT_AUDIO_PATH, model_name: str = DEFAULT_MODEL_NAME):
        # Path to the audio file to process
        self.audio_path = audio_path
        # Model variant name (e.g., 'tiny', 'base', 'small')
        self.model_name = model_name
        # Loader instance (allows future caching / device management)
        self._loader = ModelLoader(model_name)
        self._model = None  # Lazy-loaded model reference

    @property
    def model(self):
        """Access (and lazily initialize) the whisper model."""
        if self._model is None:
            self._model = self._loader.load()
        return self._model

    def load_and_prepare_audio(self):
        """Load audio from disk and create log-mel spectrogram.

        Returns:
            tuple: (raw_audio_array, mel_spectrogram_tensor)
        """
        audio = whisper.load_audio(str(self.audio_path))
        audio = whisper.pad_or_trim(audio)  # Ensure fixed length for the model
        mel = whisper.log_mel_spectrogram(audio).to(self.model.device)
        return audio, mel

    def detect_language(self, mel):
        """Run language detection on the spectrogram.

        Returns:
            tuple: (language_code, probability_dict)
        """
        _, probs = self.model.detect_language(mel)
        lang = max(probs, key=probs.get)
        return lang, probs

    def decode_audio(self, mel):
        """Decode the audio spectrogram into text using default options."""
        options = whisper.DecodingOptions()
        result = whisper.decode(self.model, mel, options)
        return result.text

    def transcribe(self):
        """Full transcription pipeline: prepare, detect language, decode.

        Returns:
            tuple: (language_code, transcription_text)
        """
        _, mel = self.load_and_prepare_audio()
        lang, _ = self.detect_language(mel)
        text = self.decode_audio(mel)
        return lang, text

