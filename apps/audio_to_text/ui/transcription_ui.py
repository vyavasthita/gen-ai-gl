
"""
transcription_ui.py
Common UI class for displaying transcription results, playback, and export options.
Used by both audio upload and microphone transcription UIs.
"""

import streamlit as st
from audio_to_text.ui.export_ui import export_pdf_button


class TranscriptionResultUI:
    """
    UI component for displaying transcription results, playback, and export options.
    Used by both audio upload and microphone transcription UIs.
    """
    def __init__(self, lang_map=None):
        """
        Initialize with optional language code map.
        Args:
            lang_map: dict mapping language codes to names
        """
        self.lang_map = lang_map or {}

    def render(self, lang, text, audio_path=None, transcription_label="Transcription"):
        """
        Display detected language, transcription, audio playback, and export options.
        Args:
            lang: language code
            text: transcription text
            audio_path: path to audio file (optional)
            transcription_label: label for transcription box
        """
        # Map language code to full name if available
        lang_full = self.lang_map.get(lang, lang) if self.lang_map else lang
        st.success(f"Detected language: {lang_full}")
        st.text_area(transcription_label, value=text, height=180)

        # Show audio playback if file provided
        if audio_path:
            st.audio(str(audio_path), format="audio/wav")
        # Use a unique key for each context to avoid Streamlit key errors
        key = "mic_pdf_download" if "Microphone" in transcription_label else "audio_pdf_download"
        export_pdf_button(text, key=key)
