import streamlit as st
try:
    from streamlit import st_autorefresh  # modern API
except ImportError:
    st_autorefresh = None
from streamlit_webrtc import webrtc_streamer, WebRtcMode, AudioProcessorBase
import streamlit_webrtc
import torch
import numpy as np
import io
import wave

from services.model_loader import load_model, DEFAULT_WHISPER
from services.transcriber import transcribe

st.set_page_config(page_title="🎤 Live Speech to Text", layout="centered")

st.title("🎤 Live Microphone → Text Transcription")
st.write("Using openai/whisper-medium with real-time microphone capture.")

# ---------------------------
# Load Model Once
# ---------------------------
@st.cache_resource
def init_model(model_name: str):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    processor, model, model_type = load_model(model_name, device)
    return processor, model, model_type, device

# Session state setup
if "model_ready" not in st.session_state:
    st.session_state.model_ready = False
if "model_tuple" not in st.session_state:
    st.session_state.model_tuple = None
if "streaming_transcript" not in st.session_state:
    st.session_state.streaming_transcript = ""
if "last_stream_chunk" not in st.session_state:
    st.session_state.last_stream_chunk = 0

st.sidebar.header("Model & Streaming Settings")
model_choice = st.sidebar.selectbox(
    "Model size", [DEFAULT_WHISPER, "openai/whisper-tiny", "openai/whisper-base", "openai/whisper-small"], index=0
)
chunk_seconds = st.sidebar.slider("Chunk length (sec)", 2, 10, 5)
vad_rms_threshold = st.sidebar.slider("Silence RMS threshold", 0.001, 0.02, 0.005, format="%f")
auto_stream = st.sidebar.checkbox("Auto stream transcription", value=False)

if not st.session_state.model_ready:
    if st.button("Load Model"):
        with st.spinner("Loading model (first time may download weights)..."):
            processor, model, model_type, device = init_model(model_choice)
        st.session_state.model_ready = True
        st.session_state.model_tuple = (processor, model, model_type, device)
else:
    processor, model, model_type, device = st.session_state.model_tuple
    st.caption(f"Model: {model_choice} • Device: {device} • streamlit-webrtc {getattr(streamlit_webrtc,'__version__','?')}")


# ---------------------------
# Audio Recording Logic
# ---------------------------
class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        self.buffer = []
        self.sample_rate = None
        self.frame_count = 0
        self.rms_window = []
    def recv_audio_frame(self, frame):
        if self.sample_rate is None:
            self.sample_rate = frame.sample_rate
        pcm = frame.to_ndarray().flatten().astype(np.float32) / 32768.0
        self.buffer.append(pcm)
        self.frame_count += 1
        # Keep small RMS window for VAD display
        rms = float((pcm ** 2).mean() ** 0.5)
        self.rms_window.append(rms)
        if len(self.rms_window) > 50:
            self.rms_window.pop(0)
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
    recent = proc.rms_window[-10:] if proc.rms_window else []
    avg_rms = sum(recent)/len(recent) if recent else 0.0
    level_display = f"{avg_rms:.3f}"
else:
    level_display = '—'
st.caption(f"Frames: {frame_count} | Rate: {sample_rate_display} | Avg RMS: {level_display} • VAD threshold {vad_rms_threshold:.3f}")

if st_autorefresh:
    st_autorefresh(interval=1500, limit=100000, key="audio-refresh")
else:
    # Fallback: lightweight manual refresh hint
    st.caption("Auto-refresh unavailable in this Streamlit version. Reload page periodically if stats don't update.")

if frame_count == 0:
    st.info("No frames yet. Steps: 1) Click 'Start' 2) Allow mic permission 3) Use Chrome/Firefox 4) Disable VPN/firewall or add TURN 5) Try different port.")

if webrtc_ctx and not webrtc_ctx.state.playing:
    st.info("Press 'Start' on the WebRTC widget and allow microphone access.")

if st.button("Reset Recording") and proc:
    proc.reset()
    st.info("Audio buffer cleared.")

playing = bool(webrtc_ctx and webrtc_ctx.state.playing)

if st.session_state.model_ready and st.button("Full Transcribe"):
    if not playing:
        st.warning("Start the stream and speak first.")
    elif not proc:
        st.warning("Audio processor not ready.")
    else:
        audio_np, sample_rate = proc.get_audio()
        if audio_np is None:
            st.warning("No audio recorded yet.")
        else:
            with st.spinner("Transcribing full buffer..."):
                text = transcribe(processor, model, audio_np, sample_rate, device=device)
            st.subheader("📝 Full Transcription")
            st.write(text)

if st.session_state.model_ready and st.button("Preview Last 3s"):
    if not playing or not proc:
        st.warning("Stream not running.")
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

# Streaming transcription logic
def stream_transcription():
    if not (st.session_state.model_ready and playing and proc):
        return
    audio_np, sample_rate = proc.get_audio()
    if audio_np is None or sample_rate is None:
        return
    chunk_len = int(sample_rate * chunk_seconds)
    total_len = len(audio_np)
    # Determine next chunk start
    start = st.session_state.last_stream_chunk
    while start + chunk_len <= total_len:
        chunk = audio_np[start:start+chunk_len]
        # VAD skip if below threshold
        rms = float((chunk ** 2).mean() ** 0.5)
        if rms >= vad_rms_threshold:
            text = transcribe(processor, model, chunk, sample_rate, device=device)
            st.session_state.streaming_transcript += (" " if st.session_state.streaming_transcript else "") + text
        start += chunk_len
    st.session_state.last_stream_chunk = start

if auto_stream:
    stream_transcription()
    if st.session_state.streaming_transcript:
        st.subheader("📝 Streaming Transcript")
        st.write(st.session_state.streaming_transcript)
    # Manual refresh button
    st.button("Force Stream Update", on_click=stream_transcription)

# Audio playback & download
if st.session_state.model_ready and st.button("Play Captured Audio"):
    if not proc or not playing:
        st.warning("Stream not running.")
    else:
        audio_np, sample_rate = proc.get_audio()
        if audio_np is None:
            st.warning("No audio captured.")
        else:
            # Convert to WAV bytes
            wav_buffer = io.BytesIO()
            with wave.open(wav_buffer, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)  # 16-bit
                wf.setframerate(sample_rate or 48000)
                # clip to [-1,1]
                pcm16 = np.clip(audio_np, -1.0, 1.0)
                pcm16 = (pcm16 * 32767).astype(np.int16)
                wf.writeframes(pcm16.tobytes())
            st.audio(wav_buffer.getvalue(), format='audio/wav')
            st.download_button("Download WAV", wav_buffer.getvalue(), file_name="capture.wav", mime="audio/wav")

st.divider()
st.subheader("🔄 Upload Audio File (Fallback)")
uploaded = st.file_uploader("Upload WAV/MP3/M4A", type=["wav", "mp3", "m4a"])
if uploaded and st.session_state.model_ready:
    import soundfile as sf
    data, sr = sf.read(io.BytesIO(uploaded.read()))
    if data.ndim > 1:
        data = data.mean(axis=1)
    with st.spinner("Transcribing uploaded file..."):
        text = transcribe(processor, model, data.astype(np.float32), sr, device=device)
    st.write(text)
elif uploaded and not st.session_state.model_ready:
    st.warning("Load model first.")

if st.button("Debug Stats"):
    st.json({
        "model_ready": st.session_state.model_ready,
        "playing": playing,
        "frames": frame_count,
        "sample_rate": sample_rate_display,
        "streaming_chunks_processed": st.session_state.last_stream_chunk,
        "streaming_transcript_chars": len(st.session_state.streaming_transcript),
        "iceConnectionState": getattr(webrtc_ctx, "ice_connection_state", None) if webrtc_ctx else None,
        "signalingState": getattr(webrtc_ctx, "signaling_state", None) if webrtc_ctx else None,
    })
