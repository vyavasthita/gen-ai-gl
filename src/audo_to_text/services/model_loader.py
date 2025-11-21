import whisper

DEFAULT_MODEL_NAME = "tiny"

def load_model(model_name: str = DEFAULT_MODEL_NAME):
    if not model_name:
        model_name = DEFAULT_MODEL_NAME
        
    return whisper.load_model(model_name)
