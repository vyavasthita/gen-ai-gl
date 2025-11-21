import tempfile
from pathlib import Path
import streamlit as st
from src.audo_to_text.services.model_loader import ModelLoader
from src.audo_to_text.services.audio_transcriber import AudioFileTranscriber

class AudioUploadTranscribeUI:
    """Handles audio file upload and transcription."""

    def __init__(self):
        if "whisper_model" not in st.session_state:
            st.session_state["whisper_model"] = ModelLoader("tiny").load()

    def file_uploader(self):
        return st.file_uploader("Upload audio file (wav/mp3)", type=["wav", "mp3"], accept_multiple_files=False)

    def transcribe_button(self):
        return st.button("Transcribe", key="upload_transcribe_btn")

    def save_uploaded_file(self, uploaded):
        if not uploaded:
            return None
        suffix = Path(uploaded.name).suffix or ".wav"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(uploaded.read())
            return Path(tmp.name)

    def run_transcription(self, tmp_path):
        model = st.session_state["whisper_model"]
        transcriber = AudioFileTranscriber(audio_path=tmp_path, model=model)
        lang, text = transcriber.transcribe()
        return lang, text

    def display(self):
        uploaded = self.file_uploader()
        if self.transcribe_button() and uploaded:
            tmp_path = self.save_uploaded_file(uploaded)
            try:
                lang, text = self.run_transcription(tmp_path)
                st.success(f"Detected language: {lang}")
                st.text_area("Transcription", value=text, height=180)
            finally:
                if tmp_path and tmp_path.exists():
                    tmp_path.unlink(missing_ok=True)
        elif uploaded is None:
            st.info("Upload an audio file to begin.")
