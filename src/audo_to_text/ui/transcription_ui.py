"""
Common UI class for displaying transcription results, playback, and export options.
Used by both audio upload and microphone transcription UIs.
"""
import streamlit as st
# File: transcription_ui.py
from  src.audo_to_text.ui.export_ui import export_dropdown


class TranscriptionResultUI:
    def __init__(self, lang_map=None):
        """
        lang_map: Optional dict for mapping language codes to names.
        """
        self.lang_map = lang_map or {}

    def render(self, lang, text, audio_path=None, transcription_label="Transcription"):
        """
        Display detected language, transcription, audio playback, and export options.
        lang: language code
        text: transcription text
        audio_path: path to audio file (optional)
        transcription_label: label for transcription box
        """
        lang_full = self.lang_map.get(lang, lang) if self.lang_map else lang
        st.success(f"Detected language: {lang_full}")
        st.text_area(transcription_label, value=text, height=180)

        if audio_path:
            st.audio(str(audio_path), format="audio/wav")
            
        export_dropdown(text)
