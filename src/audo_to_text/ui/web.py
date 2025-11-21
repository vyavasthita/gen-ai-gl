import streamlit as st
from src.audo_to_text.ui.audio_upload_ui import AudioUploadTranscribeUI
from src.audo_to_text.ui.microphone_ui import MicrophoneTranscribeUI

st.set_page_config(page_title="Transcribe", layout="centered")
st.title("Minimal Audio Transcription UI")
st.caption("Upload audio or record speech for transcription.")


def main():
	upload_ui = AudioUploadTranscribeUI()
	mic_ui = MicrophoneTranscribeUI()
	
	tab_upload, tab_mic = st.tabs(["Upload Audio", "Microphone"])
	
	with tab_upload:
		upload_ui.display()
		
	with tab_mic:
		mic_ui.display()
		
	st.caption("v0 modular UI")


if __name__ == "__main__":
	main()