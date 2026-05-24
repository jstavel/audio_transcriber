import sys
import os
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError, Error

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

            # Wait for the filename to appear in the prompt media container
            filename = Path(audio_path).name
            print(f"Waiting for {filename} to appear in prompt box...")
            page.wait_for_selector(f"ms-prompt-media:has-text('{filename}')", timeout=60000)

            # Wait logic for audio processing (watching for the processing indicator to disappear)
            page.wait_for_selector("file-card:has-text('Processing')", state="hidden", timeout=300000)

            print("Injecting prompt...")
            prompt_area = page.get_by_placeholder("Start typing a prompt to see what our models can do")
            prompt_area.fill("Transcribe this audio to org-mode format")

            print("Executing...")
            # Trigger Run
            run_button = page.locator("ms-run-button button.ctrl-enter-submits")
            run_button.wait_for(state="visible", timeout=30000)
            run_button.click()

            # Step 3.1 & 3.2: Content Stability Polling
            print("Waiting for transcription to complete (polling for stability)...")
            
            # Target the last instance of the combined-content section
            response_container = page.locator("section.combined-content").last
            run_button = page.locator("ms-run-button button.ctrl-enter-submits")

            previous_text = ""
            stable_iterations = 0
            
            while True:
                current_text = response_container.inner_text()
                
                if len(current_text) > len(previous_text) and current_text.strip():
                    previous_text = current_text
                    stable_iterations = 0
                elif len(current_text) == len(previous_text) and len(current_text) > 0:
                    stable_iterations += 1
                
                # Check exit condition: ~3 seconds of stability AND Run button is back
                if stable_iterations >= 2 and run_button.is_visible():
                    break
                    
                page.wait_for_timeout(1500)

            # Phase 4: Data Extraction & Output
            print("Extracting result...")
            result_text = response_container.inner_text()

            output_filename = f"{Path(audio_path).stem}.md"
            with open(output_filename, "w", encoding="utf-8") as f:
                f.write(result_text)
            
            print(f"Successfully saved transcription to {output_filename}")
        except (TimeoutError, Error) as e:
            print(f"\n[!] Playwright error encountered: {e}")
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
