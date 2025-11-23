
## (Docstrings removed to prevent Streamlit from displaying them)
# Import main UI entry point for each app


import streamlit as st
from utils.ui_helper import show_author_and_version
from audo_to_text.start import main as audio_to_text_main


def setup_main_page():
    """
    Configure Streamlit main page and display main title.
    """
    st.set_page_config(page_title="Gen AI Apps Suite", layout="centered")
    st.title("Gen AI Apps Suite")


def main():
    setup_main_page()
    show_author_and_version()
    # In future, add logic to select which app to run (e.g., via sidebar or config)
    # For now, run the audio_to_text app
    audio_to_text_main()


if __name__ == "__main__":
    main()
