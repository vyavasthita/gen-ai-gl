
# audio_upload_ui.py
# UI and logic for handling audio file uploads and transcription in Streamlit app

import tempfile
from pathlib import Path
import json
import streamlit as st
from audio_to_text.ui.transcription_ui import TranscriptionResultUI
from audio_to_text.services.audio_transcriber import AudioFileTranscriber


class AudioUploadHandler:
    """
    Handles file save, transcription, and download logic for audio uploads.
    - Loads Whisper model from session state
    - Saves uploaded audio files to /tmp
    - Runs transcription using Whisper
    - Persists and writes transcript
    - Offers download button
    """
    def __init__(self):
        # Whisper model is loaded in apps/main.py and stored in session_state
        pass

    def save_uploaded_file(self, uploaded):
        """
        Save uploaded audio file to /tmp path.
        Args:
            uploaded: Uploaded file object from Streamlit
        Returns:
            Path to saved file or None
        """
        if not uploaded:
            return None
        import os
        # Use file extension or default to .wav
        suffix = Path(uploaded.name).suffix or ".wav"
        tmp_path = Path("/tmp") / f"upload_{os.getpid()}{suffix}"
        with open(tmp_path, "wb") as tmp:
            tmp.write(uploaded.read())
        return tmp_path

    def run_transcription(self, tmp_path):
        """
        Run Whisper transcription on saved file.
        Args:
            tmp_path: Path to audio file
        Returns:
            (lang, text): Detected language and transcription text
        """
        import os
        assert os.path.exists(str(tmp_path)), f"Audio file not found: {tmp_path}"
        model = st.session_state["whisper_model"]
        transcriber = AudioFileTranscriber(audio_path=tmp_path, model=model)
        lang, text = transcriber.transcribe()
        return lang, text

    def persist_last_transcript(self, text: str):
        """
        Store last transcript in session state for later retrieval.
        Args:
            text: Transcription text
        """
        st.session_state["last_upload_transcript"] = text

    def write_transcription_to_file(self, text: str):
        """
        Write transcript to disk for download using FileHelper in local transcriptions dir.
        Args:
            text: Transcription text
        Returns:
            Path to saved file
        """
        file_helper = st.session_state["file_helper"]
        transcriptions_dir = Path(__file__).parent.parent / "transcriptions"
        transcriptions_dir.mkdir(exist_ok=True)
        file_path = transcriptions_dir / "upload_transcription.txt"
        file_path.write_text(text, encoding="utf-8")
        return file_path


class AudioUploadTranscribeUI:
    """
    Handles audio file upload UI and delegates logic to AudioUploadHandler.
    - Loads language map from config
    - Renders file uploader widget
    - Displays transcription and audio playback
    - Offers export/download options
    """
    def __init__(self):
        self.handler = AudioUploadHandler()
        self.language_map = self.load_language_map()
        self.transcription_ui = TranscriptionResultUI(lang_map=self.language_map)

    @staticmethod
    def load_language_map():
        """
        Load language code map from config file.
        Returns:
            dict mapping language codes to names
        """
        config_path = Path(__file__).parent.parent / "config/language_map.json"
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            # If config missing, return empty dict
            return {}

    def file_uploader(self):
        """
        Show file uploader widget for audio files.
        Returns:
            Uploaded file object or None
        """
        return st.file_uploader("Upload audio file (wav/mp3)", type=["wav", "mp3"], accept_multiple_files=False)

    def transcribe_button(self):
        """
        Show transcribe button widget (not used in auto mode).
        Returns:
            Button state (True/False)
        """
        return st.button("Transcribe", key="upload_transcribe_btn")

    def display(self):
        """
        Main display logic for upload tab.
        Shows uploader, runs transcription, displays results.
        """
        uploaded = self.file_uploader()
        if uploaded:
            self.process_uploaded_file(uploaded)
        else:
            st.info("Upload an audio file to begin.")

    def process_uploaded_file(self, uploaded):
        """
        Handle uploaded file, run transcription, and render results.
        Args:
            uploaded: Uploaded file object
        """
        tmp_path = self.handler.save_uploaded_file(uploaded)
        try:
            lang, text = self.handler.run_transcription(tmp_path)
            self.render_transcription(lang, text, tmp_path)
        finally:
            # Clean up temp file
            if tmp_path and tmp_path.exists():
                tmp_path.unlink(missing_ok=True)

    def render_transcription(self, lang, text, audio_path=None):
        """
        Show transcription, audio playback, and export buttons.
        Args:
            lang: Detected language code
            text: Transcription text
            audio_path: Path to audio file
        """
        self.transcription_ui.render(lang, text, audio_path, transcription_label="Transcription")

    def save_and_offer_download(self, text):
        """
        Persist transcript and show download button.
        Args:
            text: Transcription text
        """
        self.handler.persist_last_transcript(text)
        file_path = self.handler.write_transcription_to_file(text)
        st.download_button(
            label="Download Transcription",
            data=text,
            file_name="upload_transcription.txt",
            mime="text/plain"
        )

    def language_name(self, lang_code):
        """
        Map language code to full language name using cached map.
        Args:
            lang_code: Language code string
        Returns:
            Full language name or code if not found
        """
        return self.language_map.get(lang_code, lang_code)
