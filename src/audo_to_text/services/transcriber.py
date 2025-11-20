import torch
import numpy as np

TARGET_RATE = 16000

def _resample(audio: np.ndarray, orig_rate: int, target_rate: int = TARGET_RATE) -> np.ndarray:
    if orig_rate == target_rate:
        return audio
    # Simple linear interpolation resample (avoid extra dependencies)
    duration = audio.shape[0] / orig_rate
    target_len = int(duration * target_rate)
    x_old = np.linspace(0, duration, num=audio.shape[0], endpoint=False)
    x_new = np.linspace(0, duration, num=target_len, endpoint=False)
    return np.interp(x_new, x_old, audio).astype(np.float32)

def transcribe(processor, model, audio_np, sample_rate: int, device="cpu"):
    if audio_np is None or len(audio_np) == 0:
        return "No audio recorded!"

    if sample_rate is None:
        # Assume WebRTC default of 48000 if not provided
        sample_rate = 48000

    audio_rs = _resample(audio_np, sample_rate, TARGET_RATE)
    inputs = processor(audio_rs, sampling_rate=TARGET_RATE, return_tensors="pt")
    with torch.no_grad():
        predicted_ids = model.generate(inputs["input_features"])
    text = processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]
    return text.strip()
