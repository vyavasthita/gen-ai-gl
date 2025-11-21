import tempfile
from pathlib import Path
import streamlit as st
from src.audo_to_text.services.model_loader import ModelLoader
from src.audo_to_text.services.audio_transcriber import AudioFileTranscriber, DEFAULT_MODEL_NAME
from src.audo_to_text.services.speech_transcriber import SpeechTranscriber

st.set_page_config(page_title="Transcribe", layout="centered")
st.title("Minimal Audio Transcription UI")
st.caption("Prototype: upload a file and transcribe. Microphone support coming later.")


class AudioUploadTranscribeUI:
	"""Handles audio file upload and transcription."""

	def __init__(self):
		if "whisper_model" not in st.session_state:
			st.session_state["whisper_model"] = ModelLoader("tiny").load()

	def file_uploader(self):
		return st.file_uploader("Upload audio file (wav/mp3)", type=["wav", "mp3"], accept_multiple_files=False)

	def transcribe_button(self):
		return st.button("Transcribe", key="upload_transcribe_btn")

	def save_uploaded_file(self, uploaded):
		if not uploaded:
			return None
		suffix = Path(uploaded.name).suffix or ".wav"
		with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
			tmp.write(uploaded.read())
			return Path(tmp.name)

	def run_transcription(self, tmp_path):
		model = st.session_state["whisper_model"]
		transcriber = AudioFileTranscriber(audio_path=tmp_path, model=model)
		lang, text = transcriber.transcribe()
		return lang, text

	def display(self):
		uploaded = self.file_uploader()
		if self.transcribe_button() and uploaded:
			tmp_path = self.save_uploaded_file(uploaded)
			try:
				lang, text = self.run_transcription(tmp_path)
				st.success(f"Detected language: {lang}")
				st.text_area("Transcription", value=text, height=180)
			finally:
				if tmp_path and tmp_path.exists():
					tmp_path.unlink(missing_ok=True)
		elif uploaded is None:
			st.info("Upload an audio file to begin.")


class MicrophoneTranscribeUI:
	"""Handles microphone input (streaming placeholder)."""

	def __init__(self):
		if "speech_transcriber" not in st.session_state:
			st.session_state["speech_transcriber"] = SpeechTranscriber(model_name="tiny")
		# Reuse/upload model for single-shot mic transcription
		if "whisper_model" not in st.session_state:
			st.session_state["whisper_model"] = ModelLoader("tiny").load()

	def audio_recorder(self):
		"""Render microphone recorder component and return recorded clip (UploadedFile-like)."""
		return st.audio_input("Record speech")

	def save_clip(self, clip):
		"""Persist recorded clip to a temp file for transcription."""
		if not clip:
			return None
		# Attempt to derive suffix from MIME type (e.g., audio/wav)
		suffix = ".wav"
		if hasattr(clip, "type") and clip.type:
			if "mpeg" in clip.type:
				suffix = ".mp3"
			elif "ogg" in clip.type:
				suffix = ".ogg"
		with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
			data = clip.read()
			tmp.write(data)
			return Path(tmp.name)

	def transcribe_clip(self, path: Path):
		"""Transcribe the saved microphone recording using existing whisper model."""
		if not path:
			return None, ""
		model = st.session_state["whisper_model"]
		transcriber = AudioFileTranscriber(audio_path=path, model=model)
		lang, text = transcriber.transcribe()
		return lang, text

	def display_single_shot(self):
		"""Single-shot recording UI: record then transcribe."""
		clip = self.audio_recorder()
		if clip:
			col_rec, col_act = st.columns([1,1])
			with col_act:
				if st.button("Transcribe Recording", key="mic_transcribe_btn"):
					path = self.save_clip(clip)
					try:
						lang, text = self.transcribe_clip(path)
						st.success(f"Detected language: {lang if lang else 'unknown'}")
						st.text_area("Microphone Transcription", value=text, height=180)
					finally:
						if path and path.exists():
							path.unlink(missing_ok=True)
		else:
			st.info("Press 'Record speech' to capture audio.")

	def display(self):
		st.subheader("Microphone Speech Recognition")
		self.display_single_shot()
		st.caption("Future: add streaming with partial transcripts via WebRTC.")


def main():
	upload_ui = AudioUploadTranscribeUI()
	mic_ui = MicrophoneTranscribeUI()
	
	tab_upload, tab_mic = st.tabs(["Upload Audio", "Microphone"])
	
	with tab_upload:
		upload_ui.display()
		
	with tab_mic:
		mic_ui.display()
		
	st.caption("v0 minimal stub")


if __name__ == "__main__":
	main()