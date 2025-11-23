
# microphone_ui.py
# UI and logic for handling microphone input and transcription in Streamlit app

import tempfile
from pathlib import Path
import streamlit as st
from audio_to_text.ui.transcription_ui import TranscriptionResultUI
from audio_to_text.services.audio_transcriber import AudioFileTranscriber
from audio_to_text.services.speech_transcriber import SpeechTranscriber


class MicrophoneTranscribeUI:
    """
    Handles microphone input (single-shot recording and future streaming).
    - Loads Whisper and speech transcriber models from session state
    - Records and saves audio clips
    - Runs transcription using Whisper
    - Persists and writes transcript
    - Offers download/export options
    """

    def __init__(self):
        # Load speech transcriber if not already in session
        if "speech_transcriber" not in st.session_state:
            st.session_state["speech_transcriber"] = SpeechTranscriber(model_name="tiny")
        # Whisper model is loaded in apps/main.py and stored in session_state
        self.transcription_ui = TranscriptionResultUI()

    def audio_recorder(self):
        """
        Show microphone audio recorder widget.
        Returns:
            Recorded audio file object or None
        """
        return st.audio_input("Record speech")

    def save_clip(self, clip):
        """
        Save recorded audio clip to temp path.
        Args:
            clip: Recorded audio file object
        Returns:
            Path to saved file or None
        """
        if not clip:
            return None
        suffix = self.determine_suffix(clip)
        data = clip.read()  # read once
        return self.write_temp_file(data, suffix)

    def determine_suffix(self, clip) -> str:
        """
        Infer file suffix from mime type; default to .wav
        Args:
            clip: Recorded audio file object
        Returns:
            File extension string
        """
        suffix = ".wav"
        ctype = getattr(clip, "type", None) or ""
        if "mpeg" in ctype:
            suffix = ".mp3"
        elif "ogg" in ctype:
            suffix = ".ogg"
        return suffix

    def write_temp_file(self, data: bytes, suffix: str) -> Path:
        """
        Write bytes to a temp file and return its Path.
        Args:
            data: Audio data bytes
            suffix: File extension
        Returns:
            Path to temp file
        """
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(data)
            return Path(tmp.name)

    def transcribe_clip(self, path: Path):
        """
        Run Whisper transcription on saved clip.
        Args:
            path: Path to audio file
        Returns:
            (lang, text): Detected language and transcription text
        """
        if not path:
            return None, ""
        model = st.session_state["whisper_model"]
        transcriber = AudioFileTranscriber(audio_path=path, model=model)
        lang, text = transcriber.transcribe()
        return lang, text

    def display_single_shot(self):
        """
        Main display logic for microphone tab.
        Shows recorder, runs transcription, displays results.
        """
        clip = self.audio_recorder()
        if not clip:
            st.info("Press 'Record speech' to capture audio.")
            return
        self.process_clip(clip)

    def transcribe_action(self) -> bool:
        """
        Show transcribe button widget (not used in auto mode).
        Returns:
            Button state (True/False)
        """
        return st.button("Transcribe", key="mic_transcribe_btn")

    def process_clip(self, clip):
        """
        Handle clip saving, transcription, and render results.
        Args:
            clip: Recorded audio file object
        """
        path = self.save_clip(clip)
        if not path:
            st.error("Failed to save recording.")
            return
        try:
            lang, text = self.transcribe_clip(path)
            self.render_transcription(lang, text, audio_path=path)
        finally:
            # Clean up temp file
            if path.exists():
                path.unlink(missing_ok=True)

    def render_transcription(self, lang: str, text: str, audio_path=None):
        """
        Show transcription, audio playback, and export buttons.
        Args:
            lang: Detected language code
            text: Transcription text
            audio_path: Path to audio file
        """
        self.persist_last_transcript(text)
        # Use FileHelper from session state to save transcription
        file_helper = st.session_state.get("image_file_helper")
        if file_helper:
            file_helper.write_text_file("transcriptions", "microphone_transcription.txt", text)
        self.transcription_ui.render(lang, text, audio_path, transcription_label="Microphone Transcription")

    def persist_last_transcript(self, text: str):
        """
        Store last transcript in session state for later retrieval.
        Args:
            text: Transcription text
        """
        st.session_state["last_mic_transcript"] = text

    # Removed manual file writing; handled by FileHelper

    def display(self):
        """
        Entry point for microphone tab UI.
        Renders subheader and main display logic.
        """
        st.subheader("Microphone Speech Recognition")
        self.display_single_shot()
