import time
from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        # Launch browser in non-headless mode
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        print("Navigating to AI Studio...")
        page.goto("https://aistudio.google.com/")

        print("Please log in manually in the browser window.")
        print("Once you are logged in and see the dashboard, return here.")
        
        input("Press Enter here AFTER you have successfully logged in to save the session...")

        # Save storage state
        context.storage_state(path="auth_google.json")
        print("Authentication state saved to auth_google.json")

        browser.close()

if __name__ == "__main__":
    run()
