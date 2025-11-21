import whisper

DEFAULT_MODEL_NAME = "tiny"

class ModelLoader:
    """Simple wrapper around whisper model loading.

    Provides a class-based interface so that future configuration
    (device placement, caching, quantization, etc.) can be added
    without changing call sites. Currently minimal by design.
    """

    def __init__(self, model_name: str = DEFAULT_MODEL_NAME):
        # Store the requested model name (fallback to default if empty)
        self.model_name = model_name or DEFAULT_MODEL_NAME
        self._model = None  # Lazy-loaded model reference

    def load(self):
        """Load (or return cached) whisper model instance.

        Returns:
            The loaded whisper model.
        """
        if self._model is None:
            # Actual loading call to whisper; could extend with device logic later.
            self._model = whisper.load_model(self.model_name)
        return self._model

def load_model(model_name: str = DEFAULT_MODEL_NAME):
    """Functional access preserved for compatibility.

    Args:
        model_name: Whisper model variant (e.g. 'tiny', 'base').
    Returns:
        Loaded whisper model instance.
    """
    return ModelLoader(model_name).load()
