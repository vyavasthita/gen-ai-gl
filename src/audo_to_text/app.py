from services.transcriber import Transcriber, DEFAULT_AUDIO_PATH, DEFAULT_MODEL_NAME

def main():
    # Instantiate the Transcriber class directly (functional wrapper removed).
    transcriber = Transcriber(audio_path=DEFAULT_AUDIO_PATH, model_name=DEFAULT_MODEL_NAME)
    lang, text = transcriber.transcribe()
    print(f"Detected language: {lang}")
    print("Transcription:")
    print(text)

if __name__ == "__main__":
    main()