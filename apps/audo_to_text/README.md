### Packaged required
- brew install ffmpeg

## Python Packages
- openai-whisper
- streamlit-webrtc
- soundfile
- fpdf


### How to run

1. CLI
    - Go to root dir gen-ai-gl
    - Run poetry run python -m src.audo_to_text.cli.cli --audio ./src/audo_to_text/sample_files/first.wav

2. Streamlit UI
    - Go to root dir gen-ai-gl
    - PYTHONPATH=$(pwd) poetry run streamlit run src/audo_to_text/ui/main_ui.py --server.port 8502 --server.headless true