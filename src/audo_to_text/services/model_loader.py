from transformers import WhisperProcessor, WhisperForConditionalGeneration
import torch

# Tiny multilingual variant for faster cold start and language detection.
DEFAULT_WHISPER = "openai/whisper-tiny"

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
