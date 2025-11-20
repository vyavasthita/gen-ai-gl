import streamlit as st
try:
    from streamlit import st_autorefresh  # modern API
except ImportError:
    st_autorefresh = None
from streamlit_webrtc import webrtc_streamer, WebRtcMode, AudioProcessorBase
import streamlit_webrtc
import torch
import numpy as np

from services.model_loader import load_model
from services.transcriber import transcribe

st.set_page_config(page_title="🎤 Live Speech to Text", layout="centered")

st.title("🎤 Live Microphone → Text Transcription")
st.write("Using openai/whisper-medium with real-time microphone capture.")

# ---------------------------
# Load Model Once
# ---------------------------
@st.cache_resource
def init_model():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model_name = "openai/whisper-medium"
    processor, model, model_type = load_model(model_name, device)
    return processor, model, model_type, device

processor, model, model_type, device = init_model()
st.caption(f"Model: {model_type} • Device: {device} • streamlit-webrtc {getattr(streamlit_webrtc,'__version__','?')}")


# ---------------------------
# Audio Recording Logic
# ---------------------------
class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        self.buffer = []
        self.sample_rate = None
        self.frame_count = 0
    def recv_audio_frame(self, frame):
        if self.sample_rate is None:
            self.sample_rate = frame.sample_rate
        pcm = frame.to_ndarray().flatten().astype(np.float32) / 32768.0
        self.buffer.append(pcm)
        self.frame_count += 1
        return frame
    def get_audio(self):
        if not self.buffer:
            return None, self.sample_rate
        return np.concatenate(self.buffer), self.sample_rate
    def reset(self):
        self.buffer = []
        self.sample_rate = None
        self.frame_count = 0


st.subheader("🎙 Start Recording")

webrtc_ctx = webrtc_streamer(
    key="speech",
    mode=WebRtcMode.SENDONLY,
    audio_processor_factory=AudioProcessor,
    media_stream_constraints={
        "audio": {
            "echoCancellation": True,
            "noiseSuppression": True,
            "autoGainControl": True
        },
        "video": False
    },
    rtc_configuration={
        "iceServers": [
            {"urls": ["stun:stun.l.google.com:19302", "stun:stun1.l.google.com:19302"]}
            # Add TURN for restricted networks:
            # {"urls": ["turn:YOUR_TURN_SERVER:3478"], "username": "user", "credential": "pass"}
        ]
    },
    async_processing=True,
)

# Live buffer diagnostics
proc = webrtc_ctx.audio_processor if webrtc_ctx else None
frame_count = proc.frame_count if proc else 0
sample_rate_display = proc.sample_rate if (proc and proc.sample_rate) else '—'
if proc and proc.buffer:
    # Simple RMS
    concatenated = np.concatenate(proc.buffer[-10:]) if len(proc.buffer) > 10 else np.concatenate(proc.buffer)
    rms = float((concatenated ** 2).mean() ** 0.5)
    level_display = f"{rms:.3f}"
else:
    level_display = '—'
st.caption(f"Frames: {frame_count} | Rate: {sample_rate_display} | RMS: {level_display}")

if st_autorefresh:
    st_autorefresh(interval=1500, limit=100000, key="audio-refresh")
else:
    # Fallback: lightweight manual refresh hint
    st.caption("Auto-refresh unavailable in this Streamlit version. Reload page periodically if stats don't update.")

if frame_count == 0:
    st.info("No frames yet. Steps: 1) Click 'Start' 2) Allow mic permission 3) Use Chrome/Firefox 4) Check VPN/firewall 5) Try different port.")

if webrtc_ctx and not webrtc_ctx.state.playing:
    st.info("Press 'Start' on the WebRTC widget and allow microphone access.")

if st.button("Reset Recording") and proc:
    proc.reset()
    st.info("Audio buffer cleared.")

playing = bool(webrtc_ctx and webrtc_ctx.state.playing)

if st.button("Transcribe"):
    if not playing:
        st.warning("WebRTC stream not started. Press Start and allow mic permission.")
    elif not proc:
        st.warning("Audio processor not ready yet.")
    else:
        audio_np, sample_rate = proc.get_audio()
        if audio_np is None:
            st.warning("No audio recorded yet. Speak after starting the stream.")
        else:
            with st.spinner("Transcribing..."):
                text = transcribe(processor, model, audio_np, sample_rate, device=device)
            st.subheader("📝 Transcription:")
            st.write(text)

if st.button("Partial Preview"):
    if not playing:
        st.warning("WebRTC stream not started.")
    elif not proc:
        st.warning("Audio processor not ready.")
    else:
        audio_np, sample_rate = proc.get_audio()
        if audio_np is None:
            st.warning("No audio yet")
        else:
            if sample_rate is None:
                sample_rate = 48000
            last_samples = int(sample_rate * 3)
            clip = audio_np[-last_samples:]
            text = transcribe(processor, model, clip, sample_rate, device=device)
            st.info(text)

# -------- Upload fallback for environments blocking WebRTC --------
st.divider()
st.subheader("🔄 Upload Audio File (Fallback)")
uploaded = st.file_uploader("Upload WAV/MP3/M4A to transcribe", type=["wav", "mp3", "m4a"])
if uploaded:
    import soundfile as sf
    import io
    data, sr = sf.read(io.BytesIO(uploaded.read()))
    if data.ndim > 1:
        data = data.mean(axis=1)  # mixdown
    with st.spinner("Transcribing uploaded file..."):
        text = transcribe(processor, model, data.astype(np.float32), sr, device=device)
    st.write(text)

if st.button("Debug Stats"):
    if webrtc_ctx:
        st.json({
            "playing": webrtc_ctx.state.playing,
            "frames": frame_count,
            "sample_rate": sample_rate_display,
            "iceConnectionState": getattr(webrtc_ctx, "ice_connection_state", None),
            "signalingState": getattr(webrtc_ctx, "signaling_state", None),
        })
    else:
        st.warning("WebRTC context not initialized.")
