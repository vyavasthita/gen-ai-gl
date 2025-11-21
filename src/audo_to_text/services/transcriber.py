"""Deprecated module.

The functionality previously here has moved to:
 - audio file transcription: services/audio_transcriber.py (AudioFileTranscriber)
 - future streaming speech: services/speech_transcriber.py (SpeechTranscriber skeleton)

This shim exists to avoid immediate import errors. Remove it once all
code paths migrate to the new modules.
"""

from .audio_transcriber import AudioFileTranscriber as Transcriber  # Compatibility alias

