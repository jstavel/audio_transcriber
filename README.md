# Audio Transcriber Pipeline

Automated transcription of audio files using Playwright and Google AI Studio.

## Documentation
- [Technical Specification](docs/specification.md)
- [Implementation Plan for Next Slice](docs/implementation-plan.md)
- [Architecture Decision Records (ADRs)](docs/adr/)

## Quick Start
1. Create a virtual environment: `python -m venv venv`
2. Activate and install dependencies:
   - Linux/macOS: `source venv/bin/activate && pip install -r requirements.txt`
   - Windows: `venv\Scripts\activate && pip install -r requirements.txt`
3. Launch Chrome with debugging: `google-chrome --remote-debugging-port=9222`
4. Run transcription: `python transcribe.py your-audio.mp3`
