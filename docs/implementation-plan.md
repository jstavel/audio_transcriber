# Implementation Plan: Reliable Text Polling for LLM Generation

## 1. Context & Traceability
* **Slice Reference:** `slice-2024-XX-XX-text-polling-completion`
* **Problem Statement:** AI Studio streams text response. Even if the "Run" button returns to its idle state, the UI might still be rendering the final blocks of text or performing post-generation formatting. Simple "wait for button" logic can lead to premature scraping of incomplete transcriptions.
* **Solution Strategy:** Implement a multi-stage polling mechanism that monitors both the DOM state (the "Run" button) and the stability of the text content itself. The script will only proceed to extraction when the content length remains static over a specific observation window.

---

## 2. Technical Requirements

### Target File
* `transcribe.py`

### Logic Requirements
* Use `page.locator()` to target the most recent response message in the AI Studio chat interface.
* Implement a polling loop that captures `innerText` from the response container.

---

## 3. Step-by-Step Implementation Detail

### Step 3.1: Locate the Response Container
Identify the selector for the LLM's response output. 
* **Target Selector:** `section.combined-content` (or the specific markdown container inside the chat history).
* **Action:** Select the *last* instance of this container to ensure we are reading the current transcription.

### Step 3.2: Implement Content Stability Polling
Instead of relying solely on the "Run" button, the script must verify the text has stopped growing.
1.  **Initialize:** Set `previous_text = ""` and `stable_iterations = 0`.
2.  **Loop:** Every 1.5 seconds (using a non-blocking wait):
    *   Fetch `current_text` from the response container.
    *   If `len(current_text) > len(previous_text)` and `current_text` is not empty:
        *   Update `previous_text = current_text`.
        *   Reset `stable_iterations = 0`.
    *   Else if `len(current_text) == len(previous_text)` and `len(current_text) > 0`:
        *   Increment `stable_iterations`.
3.  **Exit Condition:** The loop terminates when `stable_iterations >= 2` (ensuring ~3 seconds of no change) AND the "Run" button is visible/enabled.

### Step 3.3: Extraction & Output
Once the stability condition is met:
*   **Action:** Perform a final fetch of the `innerText`.
*   **File I/O:** Sanitize the input filename and write the result to a `{filename}.md` file.
*   **Logging:** Output the path of the saved file and the final character count to the console.

---

## 4. Verification & Edge Cases
*   **Empty Response:** Handle cases where the LLM might fail to generate text (timeout the loop after a global limit).
*   **Late Rendering:** The 3-second stability window accounts for AI Studio's layout shifts or "thinking" pauses.
