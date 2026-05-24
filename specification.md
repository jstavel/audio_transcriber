# Specification: Proof of Work - AI Studio E2E Transcriber

## 1. Objective & Scope
The goal of the project is to create a lightweight, robust
command-line tool written in Python using Playwright. It automates
Google AI Studio to transcribe local `.mp3` audio files into formatted
Markdown text documents.

This project deliberately bypasses Google's anti-bot/2FA login mechanics
by connecting to a pre-authenticated Chrome instance via the Chrome
DevTools Protocol (CDP). It focuses entirely on local execution, browser automation,
async UI synchronization, and data extraction.

## 2. Target Workflow
1. **Manual Preparation:** User launches Google Chrome manually with remote debugging enabled (`--remote-debugging-port=9222`).
2. **Execution Phase (Automated):** The main script connects to the running Chrome instance via CDP, navigates to AI Studio, uploads a specified `.mp3`, inputs the prompt, triggers the run action, waits for the LLM to complete generation, and saves the text output to a local `.md` file.

## 3. Technology Stack
- **Language:** Python 3.11+ (Targeting Kraken QA technical requirements)
- **Framework:** Playwright for Python (Synchronous API preferred for straightforward CLI execution)
- **Connection:** Chrome DevTools Protocol (CDP) to attach to existing browser sessions.
- **Target Site:** `https://aistudio.google.com/`

## 4. Key Engineering Challenges & Solutions
- **Challenge: Google Security & 2FA blocks automated login.**
  - *Solution:* Utilize an existing authenticated browser session via Chrome DevTools Protocol (CDP) connection.
- **Challenge: UI Race Conditions (Uploading large audio files takes time).**
  - *Solution:* Explicit async wait conditions tracking the processing state of the audio waveform element before prompt submission.
- **Challenge: Dynamic text generation streaming.**
  - *Solution:* Smart pooling/waiting for the completion indicator (e.g., the Stop button switching back to Run, or specific generation status classes) combined with additional text polling to ensure the LLM has finished printing all content before extraction.

## 5. Success Criteria
- [ ] Main script handles a local `.mp3` file, automates the complete upload, prompt insertion, and trigger sequence.
- [ ] Text output is successfully scraped from the DOM and written as a file.
- [ ] No hardcoded static sleep commands are used (`page.wait_for_timeout` is banned except for extreme edge-cases).

# Implementation Plan - AI Studio E2E Transcriber

## Phase 1: Environment Setup
- [x] Initialize Python virtual environment.
- [x] Install dependencies: `playwright`.
- [x] Install Playwright browsers: `playwright install chromium`.
- [ ] Write requirements.txt

## Phase 2: Session Management (Manual Auth) [x]
- [x] Create `authenticate.py`:
    - Connect to a manually launched Chrome instance via `connect_over_cdp` on port 9222.
    - Navigate to `https://aistudio.google.com/`.
    - Wait for manual user login.

## Phase 3: Core Transcription Engine
- [ ] Create `transcribe.py`:
    - [x] Initialize Playwright with CDP connection to port 9222.
    - [x] Implement file upload logic (targeting the file input element).
    - [x] Implement wait logic for audio processing (watching for waveform/processing indicator).
    - [x] Implement prompt injection ("Transcribe this audio to Markdown").
    - [x] Implement execution trigger (click "Run").
    - [x] Implement completion polling (wait for "Run" button to be re-enabled or "Stop" to disappear).

## Phase 4: Data Extraction & Output
- [ ] Implement Text Polling to wait for the LLM to finish printing/streaming the full transcription.
- [ ] Save extracted text to `{input_filename}.md`.

## Phase 5: Verification
- [ ] Test with a short `.mp3` file.
- [ ] Verify `auth_google.json` persistence.
