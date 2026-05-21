# Specification: Proof of Work - AI Studio E2E Transcriber

## 1. Objective & Scope
The goal of Slice 1 is to create a lightweight, robust command-line tool written in Python using Playwright. It automates Google AI Studio to transcribe local `.mp3` audio files into formatted Markdown text documents.

This slice deliberately bypasses Google's anti-bot/2FA login mechanics by utilizing **Session Reuse** (importing a pre-authenticated JSON state). It focuses entirely on local execution, browser automation, async UI synchronization, and data extraction.

## 2. Target Workflow
1. **Manual Preparation:** User launches Google Chrome manually with remote debugging enabled (`--remote-debugging-port=9222`).
2. **Authentication Phase:** A script connects to the running Chrome instance via CDP, waits for the user to authenticate with Google, and dumps the cookies/local storage into `auth_google.json`.
3. **Execution Phase (Automated):** The main script starts Playwright using `auth_google.json`, navigates to AI Studio, uploads a specified `.mp3`, inputs the prompt, waits for the LLM to complete generation, and saves the text output to a local `.md` file.

## 3. Technology Stack
- **Language:** Python 3.11+ (Targeting Kraken QA technical requirements)
- **Framework:** Playwright for Python (Synchronous API preferred for straightforward CLI execution)
- **Connection:** Chrome DevTools Protocol (CDP) to attach to existing browser sessions.
- **Target Site:** `https://aistudio.google.com/`

## 4. Key Engineering Challenges & Solutions
- **Challenge: Google Security & 2FA blocks automated login.**
  - *Solution:* Isolated session state management via Playwright `storage_state`.
- **Challenge: UI Race Conditions (Uploading large audio files takes time).**
  - *Solution:* Explicit async wait conditions tracking the processing state of the audio waveform element before prompt submission.
- **Challenge: Dynamic text generation streaming.**
  - *Solution:* Smart pooling/waiting for the completion indicator (e.g., the Stop button switching back to Run, or specific generation status classes) instead of static `time.sleep()`.

## 5. Success Criteria
- [ ] `auth_google.json` is generated with valid session tokens.
- [ ] Main script handles a local `.mp3` file, automates the complete upload, prompt insertion, and trigger sequence.
- [ ] Text output is successfully scraped from the DOM and written as a file.
- [ ] No hardcoded static sleep commands are used (`page.wait_for_timeout` is banned except for extreme edge-cases).

# Implementation Plan - AI Studio E2E Transcriber

## Phase 1: Environment Setup
- [x] Initialize Python virtual environment.
- [x] Install dependencies: `playwright`.
- [x] Install Playwright browsers: `playwright install chromium`.
- [ ] Write requirements.txt

## Phase 2: Session Management (Manual Auth)
- [ ] Create `authenticate.py`:
    - Connect to a manually launched Chrome instance via `connect_over_cdp` on port 9222.
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
