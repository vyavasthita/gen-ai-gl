import tempfile
from pathlib import Path
import streamlit as st
from src.audo_to_text.services.model_loader import ModelLoader
from src.audo_to_text.services.audio_transcriber import AudioFileTranscriber
from src.audo_to_text.services.speech_transcriber import SpeechTranscriber


class MicrophoneTranscribeUI:
    """Handles microphone input (single-shot recording and future streaming)."""

    def __init__(self):
        if "speech_transcriber" not in st.session_state:
            st.session_state["speech_transcriber"] = SpeechTranscriber(model_name="tiny")
        if "whisper_model" not in st.session_state:
            st.session_state["whisper_model"] = ModelLoader("tiny").load()

    def audio_recorder(self):
        return st.audio_input("Record speech")

    def save_clip(self, clip):
        if not clip:
            return None
        suffix = self.determine_suffix(clip)
        data = clip.read()  # read once
        return self.write_temp_file(data, suffix)

    def determine_suffix(self, clip) -> str:
        """Infer file suffix from mime type; default wav."""
        suffix = ".wav"
        ctype = getattr(clip, "type", None) or ""
        if "mpeg" in ctype:
            suffix = ".mp3"
        elif "ogg" in ctype:
            suffix = ".ogg"
        return suffix

    def write_temp_file(self, data: bytes, suffix: str) -> Path:
        """Write bytes to a temp file and return its Path."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(data)
            return Path(tmp.name)

    def transcribe_clip(self, path: Path):
        if not path:
            return None, ""
        
        model = st.session_state["whisper_model"]
        transcriber = AudioFileTranscriber(audio_path=path, model=model)
        lang, text = transcriber.transcribe()
        return lang, text

    def display_single_shot(self):
        clip = self.audio_recorder()
        if not clip:
            st.info("Press 'Record speech' to capture audio.")
            return
        col_info, col_btn = st.columns([1, 1])
        with col_btn:
            if self.transcribe_action():
                self.process_clip(clip)

    def transcribe_action(self) -> bool:
        """Render and return state of transcribe button."""
        return st.button("Transcribe Recording", key="mic_transcribe_btn")

    def process_clip(self, clip):
        """Handle clip saving, transcription, display, and cleanup."""
        path = self.save_clip(clip)
        if not path:
            st.error("Failed to save recording.")
            return
        try:
            lang, text = self.transcribe_clip(path)
            self.render_transcription(lang, text)
        finally:
            if path.exists():
                path.unlink(missing_ok=True)

    def render_transcription(self, lang: str, text: str):
        """Render transcription results in UI."""
        st.success(f"Detected language: {lang if lang else 'unknown'}")
        st.text_area("Microphone Transcription", value=text, height=180)

    def display(self):
        st.subheader("Microphone Speech Recognition")
        self.display_single_shot()
        st.caption("Future: add streaming with partial transcripts via WebRTC.")
