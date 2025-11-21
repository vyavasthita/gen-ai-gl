from pathlib import Path
import whisper
from .model_loader import load_model

DEFAULT_AUDIO_PATH = Path("./src/audo_to_text/sample_files/first.wav")
DEFAULT_MODEL_NAME = "tiny"

def load_and_prepare_audio(path: Path, model):
    audio = whisper.load_audio(str(path))
    audio = whisper.pad_or_trim(audio)
    mel = whisper.log_mel_spectrogram(audio).to(model.device)
    return audio, mel

def detect_language(mel, model):
    _, probs = model.detect_language(mel)
    lang = max(probs, key=probs.get)
    return lang, probs

def decode_audio(mel, model):
    options = whisper.DecodingOptions()
    result = whisper.decode(model, mel, options)
    return result.text

def transcribe(audio_path: Path = DEFAULT_AUDIO_PATH, model_name: str = DEFAULT_MODEL_NAME):
    model = load_model(model_name)
    _, mel = load_and_prepare_audio(audio_path, model)
    lang, _ = detect_language(mel, model)
    text = decode_audio(mel, model)
    return lang, text

def main():
    lang, text = transcribe()
    print(f"Detected language: {lang}")
    print("Transcription:")
    print(text)

if __name__ == "__main__":
    main()
