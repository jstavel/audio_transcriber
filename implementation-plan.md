# Implementation Plan - Slice 1: AI Studio E2E Transcriber

## Phase 1: Environment Setup
- [x] Initialize Python virtual environment.
- [x] Install dependencies: `playwright`.
- [x] Install Playwright browsers: `playwright install chromium`.
- [x] Create requirements.txt

## Phase 2: Session Management (Manual Auth)
- [ ] Create `authenticate.py`:
    - Launch Chromium in non-headless mode.
    - Navigate to `https://aistudio.google.com/`.
    - Wait for manual user login.
    - Save storage state to `auth_google.json` using `context.storage_state()`.

## Phase 3: Core Transcription Engine
- [ ] Create `transcribe.py`:
    - Initialize Playwright with `storage_state="auth_google.json"`.
    - Implement file upload logic (targeting the file input element).
    - Implement wait logic for audio processing (watching for waveform/processing indicator).
    - Implement prompt injection ("Transcribe this audio to Markdown").
    - Implement execution trigger (click "Run").
    - Implement completion polling (wait for "Run" button to be re-enabled or "Stop" to disappear).

## Phase 4: Data Extraction & Output
- [ ] Logic to locate the result text in the DOM.
- [ ] Save extracted text to `{input_filename}.md`.

## Phase 5: Verification
- [ ] Test with a short `.mp3` file.
- [ ] Verify `auth_google.json` persistence.
