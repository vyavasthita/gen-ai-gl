"""
Main UI entry point for audio/speech transcription app.
Provides tabbed interface for file upload and microphone input.
"""
import streamlit as st
from src.audo_to_text.ui.audio_upload_ui import AudioUploadTranscribeUI
from src.audo_to_text.ui.microphone_ui import MicrophoneTranscribeUI
from src.audo_to_text.utils.file_helper import FileHelper

# Setup Streamlit page configuration and header

def setup_page():
    """Configure Streamlit page and display main header/caption."""
    st.set_page_config(page_title="Transcribe", layout="centered")
    st.title("Minimal Audio Transcription UI")
    st.caption("Upload audio or record speech for transcription.")

def setup_file_helper():
    """Initialize FileHelper once at app startup."""
    if "file_helper" not in st.session_state:
        st.session_state["file_helper"] = FileHelper()

def setup_whisper_model():
    """Initialize Whisper model once at app startup."""
    from src.audo_to_text.services.model_loader import ModelLoader
    if "whisper_model" not in st.session_state:
        st.session_state["whisper_model"] = ModelLoader("tiny").load()

setup_page()
setup_file_helper()
setup_whisper_model()

# Main application logic

def main():
    """Render tabbed UI for audio upload and microphone transcription."""
    upload_ui = AudioUploadTranscribeUI()  # UI for file upload
    mic_ui = MicrophoneTranscribeUI()      # UI for microphone input
    
    tab_upload, tab_mic = st.tabs(["Upload Audio", "Microphone"])
    
    with tab_upload:
        upload_ui.display()  # Show upload UI
    
    with tab_mic:
        mic_ui.display()     # Show microphone UI

if __name__ == "__main__":
    main()