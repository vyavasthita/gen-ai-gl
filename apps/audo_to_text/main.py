
"""
main.py
Main UI entry point for audio/speech transcription app.
Provides tabbed interface for file upload and microphone input.
"""

import streamlit as st
import toml
from ui.audio_upload_ui import AudioUploadTranscribeUI
from ui.microphone_ui import MicrophoneTranscribeUI
from utils.file_helper import FileHelper

# ---------- Setup Functions ----------
def setup_page():
    """
    Configure Streamlit page and display main header/caption.
    Sets page title, layout, and main caption.
    """
    st.set_page_config(page_title="Transcribe", layout="centered")
    st.title("Minimal Audio Transcription UI")
    st.caption("Upload audio or record speech for transcription.")

def show_author_and_version():
    """
    Show author and version in bold at the top of the main UI.
    Reads version from pyproject.toml if available.
    """
    try:
        pyproject = toml.load("pyproject.toml")
        version = pyproject["project"]["version"]
    except Exception:
        # Fallback to default version if file missing or unreadable
        version = "0.1.0"
    st.markdown("**Author:** Dilip Sharma")
    st.markdown(f"**Version:** {version}")

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
    from services.model_loader import ModelLoader
    if "whisper_model" not in st.session_state:
        st.session_state["whisper_model"] = ModelLoader("tiny").load()

# ---------- App Initialization ----------
setup_page()
show_author_and_version()
setup_file_helper()
setup_whisper_model()

# ---------- Main Application Logic ----------
def main():
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

# ---------- Entry Point ----------
if __name__ == "__main__":
    main()
