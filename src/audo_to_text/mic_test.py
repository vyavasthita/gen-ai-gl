import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, AudioProcessorBase
import streamlit_webrtc
import numpy as np

st.set_page_config(page_title="🔊 Mic Test", layout="centered")
st.title("🔊 Minimal Microphone Frame Test")
st.caption(f"streamlit-webrtc {getattr(streamlit_webrtc,'__version__','?')} • Simple frame counter")

class TestAudioProcessor(AudioProcessorBase):
    def __init__(self):
        self.frames = 0
        self.rate = None
        self.rms = 0.0
    def recv_audio_frame(self, frame):
        if self.rate is None:
            self.rate = frame.sample_rate
        pcm = frame.to_ndarray().flatten().astype(np.float32) / 32768.0
        self.rms = float((pcm ** 2).mean() ** 0.5)
        self.frames += 1
        return frame
    def stats(self):
        return {
            "frames": self.frames,
            "sample_rate": self.rate,
            "rms": self.rms,
        }

st.subheader("Start WebRTC Stream")
webrtc_ctx = webrtc_streamer(
    key="mic-test",
    mode=WebRtcMode.SENDONLY,
    audio_processor_factory=TestAudioProcessor,
    media_stream_constraints={"audio": True, "video": False},
    rtc_configuration={
        "iceServers": [
            {"urls": ["stun:stun.l.google.com:19302", "stun:stun1.l.google.com:19302"]}
        ]
    },
    async_processing=True,
)

proc = webrtc_ctx.audio_processor if webrtc_ctx else None
playing = bool(webrtc_ctx and webrtc_ctx.state.playing)

col1, col2, col3 = st.columns(3)
with col1: st.metric("Playing", "Yes" if playing else "No")
if proc:
    stats = proc.stats()
    with col2: st.metric("Frames", stats["frames"])
    with col3: st.metric("RMS", f"{stats['rms']:.3f}")
else:
    with col2: st.metric("Frames", 0)
    with col3: st.metric("RMS", "-")

st.caption("If frames stay 0: allow mic permission, try Chrome/Firefox, disable VPN, or add TURN server.")

if st.button("Reset") and proc:
    proc.frames = 0
    proc.rms = 0.0
    st.success("Counters reset.")

