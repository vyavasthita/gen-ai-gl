"""
start.py
Entry point for the Audio to Text Streamlit UI app.
Handles all UI logic for audio upload and microphone transcription.
"""

import streamlit as st
import toml
from audo_to_text.ui.audio_upload_ui import AudioUploadTranscribeUI
from audo_to_text.ui.microphone_ui import MicrophoneTranscribeUI
from audo_to_text.utils.file_helper import FileHelper

# ---------- Setup Functions ----------

# Remove generic page config and main title; set only app-specific subtitle
def setup_audio_to_text_header():
    """
    Display Audio to Text app subtitle and author/version info.
    """
    st.header("Audio to Text Converter")


def setup_file_helper():
    """
    Initialize FileHelper once at app startup and store in session_state.
    """
    if "file_helper" not in st.session_state:
        st.session_state["file_helper"] = FileHelper()

def setup_whisper_model():
    """
    Initialize Whisper model once at app startup and store in session_state.
    """
    from audo_to_text.services.model_loader import ModelLoader
    if "whisper_model" not in st.session_state:
        st.session_state["whisper_model"] = ModelLoader("tiny").load()

# ---------- App Initialization ----------

def initialize_audio_to_text_app():
    setup_audio_to_text_header()
    setup_file_helper()
    setup_whisper_model()

# ---------- Main Application Logic ----------
def run_audio_to_text_ui():
    """
    Render tabbed UI for audio upload and microphone transcription.
    Creates two tabs: one for file upload, one for microphone input.
    """
    upload_ui = AudioUploadTranscribeUI()  # UI for file upload
    mic_ui = MicrophoneTranscribeUI()      # UI for microphone input

    tab_upload, tab_mic = st.tabs(["Upload Audio", "Microphone"])

    with tab_upload:
        upload_ui.display()  # Show upload UI

    with tab_mic:
        mic_ui.display()     # Show microphone UI

# ---------- Entry Point for Import ----------

def main():
    initialize_audio_to_text_app()
    run_audio_to_text_ui()

if __name__ == "__main__":
    main()
