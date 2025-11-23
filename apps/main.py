import streamlit as st
from utils.file_helper import FileHelper
from utils.ui_helper import show_author_and_version
from audio_to_text.start import main as audio_to_text_main


def setup_main_page():
    """
    Configure Streamlit main page and display main title.
    """
    st.set_page_config(page_title="Gen AI Apps Suite", layout="centered")
    st.title("Gen AI Apps Suite")

def setup_file_helper():
    """
    Initialize FileHelper once at app startup and store in session_state.
    """
    if "file_helper" not in st.session_state:
        st.session_state["file_helper"] = FileHelper("audio_to_text", resource_root="/tmp/resources")

def main():
    setup_main_page()
    show_author_and_version()
    setup_file_helper()
    audio_to_text_main()


if __name__ == "__main__":
    main()