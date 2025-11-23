"""Command-line interface for audio transcription.

Usage:
	python apps/audo_to_text/cli/cli.py --audio path/to/file.wav --model tiny

In future this can be extended with options (device selection, decoding
parameters, batch directories, output formats, JSON export, etc.).
"""
from __future__ import annotations
import argparse
from pathlib import Path
from audio_to_text.services.model_loader import ModelLoader
from audio_to_text.services.audio_transcriber import AudioFileTranscriber, DEFAULT_AUDIO_PATH, DEFAULT_MODEL_NAME


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(description="Whisper audio file transcription")
	parser.add_argument("--audio", type=Path, default=DEFAULT_AUDIO_PATH, help="Path to input audio file")
	parser.add_argument("--model", type=str, default=DEFAULT_MODEL_NAME, help="Whisper model variant (tiny/base/small/...)" )
	return parser.parse_args()


def main():
	args = parse_args()
	model = ModelLoader(args.model).load()
	transcriber = AudioFileTranscriber(audio_path=args.audio, model=model)
	lang, text = transcriber.transcribe()
	print(f"Language: {lang}")
	print("--- Transcript ---")
	print(text)


if __name__ == "__main__":
	main()
