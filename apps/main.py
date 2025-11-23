import streamlit as st
from utils.file_helper import FileHelper
from utils.ui_helper import show_author_and_version
from audio_to_text.start import main as audio_to_text_main
from image_to_text.start import main as image_to_text_main


def setup_main_page():
    """
    Configure Streamlit main page and display main title.
    """
    st.set_page_config(page_title="Gen AI Apps Suite", layout="wide")
    st.markdown("""
        <div style='margin-top:-40px;'></div>
        <h1 style='text-align: center; margin-bottom: 0px;'>Gen AI Apps Suite</h1>
    """, unsafe_allow_html=True)

def setup_file_helper():
    """
    Initialize FileHelper once at app startup and store in session_state.
    """
    if "file_helper" not in st.session_state:
        st.session_state["file_helper"] = FileHelper("audio_to_text", resource_root="/tmp/resources")

def init():
    """
    Initialize main app components.
    """
    setup_main_page()
    show_author_and_version()
    setup_file_helper()

def main():
    init()

    # Horizontal two-column layout for both apps with a vertical separator
    col_image, col_sep, col_audio = st.columns([1, 0.05, 1])
    with col_image:
        st.markdown("""
            <div style='text-align: center;'>
                <h3 style='display: inline-block; margin-bottom: 0px;'>Image to Text</h3><br>
                <hr style='border:1px solid #DDD; width: 180px; margin: 8px auto 20px auto;'>
            </div>
        """, unsafe_allow_html=True)
        image_to_text_main()
    with col_sep:
        st.markdown("<div style='border-left:2px solid #DDD;height:100vh;'></div>", unsafe_allow_html=True)
    with col_audio:
        st.markdown("""
            <div style='text-align: center;'>
                <h3 style='display: inline-block; margin-bottom: 0px;'>Audio to Text</h3><br>
                <hr style='border:1px solid #DDD; width: 180px; margin: 8px auto 20px auto;'>
            </div>
        """, unsafe_allow_html=True)
        audio_to_text_main()


if __name__ == "__main__":
    main()