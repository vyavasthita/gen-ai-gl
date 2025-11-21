from services.audio_transcriber import AudioFileTranscriber, DEFAULT_AUDIO_PATH, DEFAULT_MODEL_NAME
from services.model_loader import ModelLoader


def main():
    # Preload model centrally (enables reuse and one-time device init)
    model = ModelLoader(DEFAULT_MODEL_NAME).load()
    transcriber = AudioFileTranscriber(audio_path=DEFAULT_AUDIO_PATH, model=model)
    lang, text = transcriber.transcribe()
    print(f"Detected language: {lang}")
    print("Transcription:")
    print(text)


if __name__ == "__main__":
    main()