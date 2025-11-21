"""Skeleton for future real-time / streaming speech transcription.

This module anticipates a Streamlit + WebRTC implementation. The design
sketch below separates concerns for buffering, VAD (voice activity
detection), chunk assembly, and decode scheduling. Actual logic is left
as placeholders to be filled when live audio capture is introduced.

Planned components:
- SpeechTranscriber: orchestrates buffering frames and triggering decode.
- AudioBuffer: lightweight ring or append buffer (could move to utils/ later).
- VAD logic (placeholder): to decide when to segment speech.
- decode_strategy: could allow partial (streaming) vs full decode.

You will integrate with streamlit-webrtc or similar later by feeding PCM
frames into add_frame().
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Tuple
import numpy as np
import whisper
from .model_loader import ModelLoader


# Placeholder constants (tweak later once real streaming is added)
TARGET_RATE = 16000  # Whisper expected sample rate
MIN_CHUNK_SECONDS = 3.0  # Minimum audio duration before attempting decode
SILENCE_THRESHOLD = 0.01  # RMS threshold heuristic for silence


@dataclass
class AudioBuffer:
    """Simple audio buffer accumulating float32 samples at TARGET_RATE."""
    samples: List[np.ndarray] = field(default_factory=list)
    total_len: int = 0

    def append(self, pcm: np.ndarray):
        if pcm.dtype != np.float32:
            pcm = pcm.astype(np.float32)
        self.samples.append(pcm)
        self.total_len += pcm.shape[0]

    def duration(self) -> float:
        return self.total_len / TARGET_RATE if TARGET_RATE else 0.0

    def rms(self) -> float:
        if self.total_len == 0:
            return 0.0
        concat = self.to_array()
        return float(np.sqrt(np.mean(concat ** 2)))

    def to_array(self) -> np.ndarray:
        if not self.samples:
            return np.zeros(0, dtype=np.float32)
        return np.concatenate(self.samples, axis=0)

    def clear(self):
        self.samples.clear()
        self.total_len = 0

class SpeechTranscriber:
    """Prototype for future streaming speech-to-text.

    Usage pattern (future Streamlit integration):
        stt = SpeechTranscriber(model_name="tiny")
        stt.add_frame(pcm_chunk, sample_rate=48000)
        partial = stt.maybe_partial_decode()
        final = stt.finalize_if_complete()

    Currently only structural placeholders are implemented.
    """

    def __init__(self, model_name: str = "tiny"):
        self.model_name = model_name
        self._loader = ModelLoader(model_name)
        self._model = None
        self._buffer = AudioBuffer()
        self._last_transcript: Optional[str] = None

    @property
    def model(self):
        if self._model is None:
            self._model = self._loader.load()
        return self._model

    def add_frame(self, pcm: np.ndarray, sample_rate: int):
        """Add raw PCM samples for a captured frame.

        Resamples if needed (naive implementation placeholder). Actual WebRTC
        frames often arrive at 48000 Hz, so we will downsample to TARGET_RATE.
        """
        if sample_rate != TARGET_RATE and pcm.size > 0:
            # Simple linear resample (placeholder; replace with scipy or resampy later)
            duration = pcm.shape[0] / sample_rate
            target_len = int(duration * TARGET_RATE)
            x_old = np.linspace(0, duration, num=pcm.shape[0], endpoint=False)
            x_new = np.linspace(0, duration, num=target_len, endpoint=False)
            pcm = np.interp(x_new, x_old, pcm).astype(np.float32)
            
        self._buffer.append(pcm)

    def has_sufficient_audio(self) -> bool:
        return self._buffer.duration() >= MIN_CHUNK_SECONDS

    def is_silence(self) -> bool:
        return self._buffer.rms() < SILENCE_THRESHOLD

    def maybe_partial_decode(self) -> Optional[str]:
        """Attempt a partial decode if enough audio present.

        In a real implementation you might gate on both duration and
        recent activity pattern to avoid premature decodes.
        """
        if not self.has_sufficient_audio():
            return None
        
        concat = self._buffer.to_array()
        mel = whisper.log_mel_spectrogram(concat).to(self.model.device)
        
        # For partial decode, you could set no_speech_threshold lower or temperature variations.
        options = whisper.DecodingOptions()
        result = whisper.decode(self.model, mel, options)
        self._last_transcript = result.text
        return self._last_transcript

    def finalize_if_complete(self) -> Optional[str]:
        """Heuristic finalization: if buffer is silent after speech, finalize.

        Real logic would track trailing silence duration and segmentation.
        Currently returns last transcript if silence detected.
        """
        if self.is_silence() and self._last_transcript:
            final = self._last_transcript
            self._buffer.clear()
            self._last_transcript = None
            return final
        
        return None

    def force_decode(self) -> str:
        """Force a decode on current buffer regardless of duration/silence."""
        concat = self._buffer.to_array()

        if concat.size == 0:
            return ""
        
        mel = whisper.log_mel_spectrogram(concat).to(self.model.device)
        options = whisper.DecodingOptions()
        result = whisper.decode(self.model, mel, options)
        return result.text
