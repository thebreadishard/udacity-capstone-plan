from playwright.sync_api import sync_playwright
import time
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://share.gemini.google/iSDcNkLXMVQk")
    time.sleep(3)
    text = page.locator("body").inner_text()
    with open("gemini_context.txt", "w", encoding="utf-8") as f:
        f.write(text)
    browser.close()
