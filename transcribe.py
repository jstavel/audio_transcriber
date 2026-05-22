import sys
import os
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError

def transcribe(audio_path):
    with sync_playwright() as p:
        # Connect to an already running instance of Chrome
        print("Connecting to existing Chrome instance on port 9222...")
        try:
            browser = p.chromium.connect_over_cdp("http://localhost:9222")
        except Exception as e:
            print(f"Error: Could not connect to Chrome. Make sure it's running with --remote-debugging-port=9222. {e}")
            return

        context = browser.contexts[0]
        page = context.new_page()

        try:
            print(f"Navigating to AI Studio...")
            page.goto("https://aistudio.google.com/")

            # Phase 3: Core Transcription Engine
            print(f"Uploading {audio_path}...")
            
            # Target the stable media button identified in debug artifacts
            add_media_button = page.locator("//ms-add-media-button//button")
            add_media_button.wait_for(state="visible", timeout=30000)
            
            # Open the media menu
            add_media_button.click()

            # Target the "Upload files" menu item that appears in the overlay
            upload_item = page.locator("//button[contains(@class, 'upload-file-menu-item')]")
            upload_item.wait_for(state="visible", timeout=10000)
            
            # Use expect_file_chooser to handle the file upload interaction
            with page.expect_file_chooser() as fc_info:
                upload_item.click()
            file_chooser = fc_info.value
            file_chooser.set_files(audio_path)

            # Wait logic for audio processing (watching for the processing indicator to disappear or waveform to appear)
            # In AI Studio, the file card usually shows a 'Processing' state. 
            # We wait for the 'Cancel' button or progress bar on the file card to disappear.
            page.wait_for_selector("file-card:has-text('Processing')", state="hidden", timeout=300000)

            print("Injecting prompt...")
            prompt_area = page.get_by_placeholder("Type something")
            prompt_area.fill("Transcribe this audio to org-mode format")

            print("Executing...")
            # Trigger Run
            run_button = page.get_by_role("button", name="Run")
            run_button.click()

            # Completion polling: Wait for the 'Stop' button to disappear and 'Run' to be available
            page.wait_for_selector("button:has-text('Stop')", state="hidden", timeout=600000)
            
            # Phase 4: Data Extraction & Output
            print("Extracting result...")
            # Result text is typically in a markdown-renderer or specific output div
            result_locator = page.locator("div.model-response-text")
            result_text = result_locator.inner_text()

            output_filename = f"{Path(audio_path).stem}.md"
            with open(output_filename, "w", encoding="utf-8") as f:
                f.write(result_text)
            
            print(f"Successfully saved transcription to {output_filename}")
        except TimeoutError as e:
            print(f"\n[!] Timeout encountered: {e}")
            print("Generating debug artifacts...")
            
            # Step 3.1: Visual State Capture
            page.screenshot(path="debug_screenshot.png", full_page=True)
            
            # Step 3.2: DOM Querying & Filtering via JavaScript Injection
            elements = page.evaluate("""() => {
                const results = [];
                const interactiveTags = ['BUTTON', 'INPUT', 'A', 'TEXTAREA'];
                const keywords = ['+', 'upload', 'add', 'file', 'insert', 'media'];
                
                const allElements = document.querySelectorAll('*');
                allElements.forEach(el => {
                    const rect = el.getBoundingClientRect();
                    const isVisible = rect.width > 0 && rect.height > 0 && 
                                    getComputedStyle(el).visibility !== 'hidden' && 
                                    getComputedStyle(el).display !== 'none';
                    
                    if (!isVisible) return;

                    const tag = el.tagName;
                    const text = (el.innerText || el.getAttribute('aria-label') || el.getAttribute('title') || el.getAttribute('placeholder') || '').toLowerCase();
                    const id = el.id.toLowerCase();
                    const className = el.className.toString().toLowerCase();

                    const matchesTag = interactiveTags.includes(tag);
                    const matchesKeyword = keywords.some(k => 
                        text.includes(k) || id.includes(k) || className.includes(k)
                    );

                    if (matchesTag || matchesKeyword) {
                        results.push({
                            tag: tag,
                            text: el.innerText || el.getAttribute('aria-label') || el.getAttribute('title') || '',
                            id: el.id,
                            class: el.className.toString(),
                            selector: el.id ? `#${el.id}` : `${tag.toLowerCase()}.${el.className.toString().replace(/\\s+/g, '.')}`
                        });
                    }
                });
                return results;
            }""")

            # Step 3.3: Output Generation
            with open("debug_elements.txt", "w", encoding="utf-8") as f:
                for el in elements:
                    f.write("================================================================================\n")
                    tag = el['tag']
                    text = el['text'].strip()
                    f.write(f'[{tag}] "{text}"\n')
                    f.write("================================================================================\n")
                    f.write(f"ID:        {el['id']}\n")
                    f.write(f"Class:     {el['class']}\n")
                    f.write(f"Selector:  {el['selector']}\n")
                    f.write("--------------------------------------------------------------------------------\n\n")

            print("\nDIAGNOSTIC WARNING: Automation stopped due to timeout.")
            print("Check 'debug_screenshot.png' and 'debug_elements.txt' for UI state analysis.")
        browser.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python transcribe.py <path_to_audio_file>")
    else:
        transcribe(sys.argv[1])
