import tempfile
from pathlib import Path
import json
import streamlit as st
from src.audo_to_text.ui.transcription_ui import TranscriptionResultUI
from src.audo_to_text.services.model_loader import ModelLoader
from src.audo_to_text.services.audio_transcriber import AudioFileTranscriber


class AudioUploadHandler:
    """
    Handles file save, transcription, and download logic for audio uploads.
    - Loads Whisper model
    - Saves uploaded audio files
    - Runs transcription
    - Persists and writes transcript
    - Offers download button
    """
    def __init__(self):
        # Load Whisper model if not already in session
        if "whisper_model" not in st.session_state:
            st.session_state["whisper_model"] = ModelLoader("tiny").load()

    def save_uploaded_file(self, uploaded):
        """Save uploaded audio file to temp path."""
        if not uploaded:
            return None
        suffix = Path(uploaded.name).suffix or ".wav"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(uploaded.read())
            return Path(tmp.name)

    def run_transcription(self, tmp_path):
        """Run Whisper transcription on saved file."""
        model = st.session_state["whisper_model"]
        transcriber = AudioFileTranscriber(audio_path=tmp_path, model=model)
        lang, text = transcriber.transcribe()

        return lang, text

    def persist_last_transcript(self, text: str):
        """Store last transcript in session state."""
        st.session_state["last_upload_transcript"] = text

    def write_transcription_to_file(self, text: str):
        """Write transcript to disk for download."""
        out_dir = Path("transcriptions")
        out_dir.mkdir(exist_ok=True)
        file_path = out_dir / "upload_transcription.txt"
        file_path.write_text(text, encoding="utf-8")
        return file_path

    def download_button(self, text: str, file_path: Path):
        """Show download button for transcript text."""
        pass


class AudioUploadTranscribeUI:
    """
    Handles audio file upload UI and delegates logic to AudioUploadHandler.
    - Loads language map
    - Renders file uploader and transcribe button
    - Displays transcription and audio playback
    - Offers export/download options
    """
    def __init__(self):
        self.handler = AudioUploadHandler()
        self.language_map = self.load_language_map()
        self.transcription_ui = TranscriptionResultUI(lang_map=self.language_map)

    @staticmethod
    def load_language_map():
        """Load language code map from config file."""

        config_path = Path(__file__).parent.parent / "config/language_map.json"
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def file_uploader(self):
        """Show file uploader widget."""
        return st.file_uploader("Upload audio file (wav/mp3)", type=["wav", "mp3"], accept_multiple_files=False)

    def transcribe_button(self):
        """Show transcribe button widget."""
        return st.button("Transcribe", key="upload_transcribe_btn")

    def display(self):
        """Main display logic for upload tab."""
        uploaded = self.file_uploader()
        
        if self.transcribe_button() and uploaded:
            self.process_uploaded_file(uploaded)
        elif uploaded is None:
            st.info("Upload an audio file to begin.")

    def process_uploaded_file(self, uploaded):
        """Handle uploaded file, run transcription, and render results."""
        tmp_path = self.handler.save_uploaded_file(uploaded)
        try:
            lang, text = self.handler.run_transcription(tmp_path)
            self.render_transcription(lang, text, tmp_path)
        finally:
            if tmp_path and tmp_path.exists():
                tmp_path.unlink(missing_ok=True)

    def render_transcription(self, lang, text, audio_path=None):
        """Show transcription, audio playback, and export buttons."""
        self.save_and_offer_download(text)
        self.transcription_ui.render(lang, text, audio_path, transcription_label="Transcription")

    def save_and_offer_download(self, text):
        """Persist transcript and show download button."""
        self.handler.persist_last_transcript(text)
        file_path = self.handler.write_transcription_to_file(text)
        self.handler.download_button(text, file_path)

    def language_name(self, lang_code):
        """Map language code to full language name using cached map."""
        return self.language_map.get(lang_code, lang_code)
