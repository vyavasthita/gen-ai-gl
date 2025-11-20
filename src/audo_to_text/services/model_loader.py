from transformers import WhisperProcessor, WhisperForConditionalGeneration
import torch

# Tiny English-only variant for faster cold start.
DEFAULT_WHISPER = "openai/whisper-tiny.en"

def load_model(model_name: str = DEFAULT_WHISPER, device: str = "cpu"):
    if not model_name:
        model_name = DEFAULT_WHISPER
    processor = WhisperProcessor.from_pretrained(model_name)
    kwargs = {"low_cpu_mem_usage": True}
    if device == "cuda":
        kwargs["torch_dtype"] = torch.float16
    model = WhisperForConditionalGeneration.from_pretrained(model_name, **kwargs)
    model.to(device)
    return processor, model, "whisper"
