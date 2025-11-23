# gen-ai-gl

### Packaged required
- brew install ffmpeg

## Python Packages
- openai-whisper
- soundfile
- fpdf


### How to run

1. CLI
    - Go to dir 'gen-ai-gl/apps'
    - Run following command
        - poetry run python -m audio_to_text.cli.cli --audio audio_to_text/sample_files/first.wav

2. Streamlit UI
    - Export Following environment variables
        - export STREAMLIT_SERVER_PORT=8502
        - export STREAMLIT_SERVER_HEADLESS=true
    - Go to dir 'gen-ai-gl/apps'
    - poetry run streamlit run main.py