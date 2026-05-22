# Implementation Plan: Robust Offline Debugging for Selector Timeouts

## 1. Context & Traceability
* **Slice Reference:** `slice-2026-05-22-cdp-debug-artifacts`
* **Problem Statement:** The script `transcribe.py` successfully connects to Google AI Studio via CDP, but fails to interact with the file upload interface (the "+" button) due to unstable, dynamic, or updated DOM selectors. High-frequency UI shifts in AI Studio make manual/live debugging inefficient.
* **Solution Strategy:** Implement a diagnostic "black box" inside the automation script. Upon a selector timeout, the script will automatically capture the exact state of the application in two local files (`debug_screenshot.png` and `debug_elements.txt`), enabling rapid offline analysis and XPath/CSS selector refinement.

---

## 2. Technical Requirements

### Target File
* `transcribe.py`

### Exception Boundaries
* Intercept `playwright.async_api.TimeoutError`.
* The `try...except` block must safely wrap all browser interaction steps following the successful initialization of the page context via CDP.

---

## 3. Step-by-Step Implementation Detail

### Step 3.1: Visual State Capture
Immediately upon catching the `TimeoutError`, capture the full visual state of the web application.
* **Action:** Trigger a full-page screenshot.
* **Output Target:** Local file `debug_screenshot.png` in the script's root directory.

### Step 3.2: DOM Querying & Filtering via JavaScript Injection
To prevent unreadable and bloated HTML dumps, use `page.evaluate()` to run a custom filtering script inside the browser context.

#### Selection Strategy (The Filter Criteria):
The script must look for elements that meet **at least one** of these structural conditions:
1. **Interactive Tags:** All `button`, `input`, `a`, and `textarea` tags.
2. **Context-Specific Keywords:** Any visible element containing the character `"+"`, or strings matching `"upload"`, `"add"`, `"file"`, `"insert"`, `"media"` inside its text content, `aria-label`, `title`, `id`, or `class` attributes.
3. **Visibility Constraint:** The element must be rendered and visible. Filter out elements with `display: none`, `visibility: hidden`, or where `getBoundingClientRect()` returns zero width/height.

#### Data Extraction (Per Element):
For each matching element, harvest the following metadata properties:
* **Tag:** `element.tagName`
* **Text/Label:** Prioritize `element.innerText`, falling back to `aria-label`, `title`, or `placeholder` attributes.
* **Identifiers:** `id` and `className`.
* **Inferred Selector:** Generate a robust CSS selector or a direct XPath strategy (e.g., `//button[contains(text(), 'Add')]` or combined class paths) to aid offline selection.

### Step 3.3: Output Generation & Graceful Termination
* **File Target:** `debug_elements.txt`
* **Format Structure:**
  
```text
  ================================================================================
  [TAG] "Extracted Text / Aria-Label"
  ================================================================================
  ID:        <element_id>
  Class:     <element_classes>
  Selector:  <css_or_xpath_strategy>
  --------------------------------------------------------------------------------
```
* **Console Logging**: Print a highly visible terminal message
  alerting the user that execution stopped, pointing explicitly to the
  generated debug_screenshot.png and debug_elements.txt.

* Cleanly close browser hooks if applicable or exit the runtime process.


