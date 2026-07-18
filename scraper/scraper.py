import os
import time
import json
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

def run():
    session_dir = os.path.abspath("./udacity_session")
    
    # We start strictly at the APA Resources module
    start_url = "https://learn.udacity.com/cd001-capstone?version=1.5.1&lessonKey=df676f57-9d04-4a77-b99a-f7ae48dad63c&conceptKey=26f74300-dd9a-4416-9a74-6ceae6a2e5ec"
    
    with sync_playwright() as p:
        print(f"Loading persistent session at {session_dir}...")
        
        context = p.chromium.launch_persistent_context(
            user_data_dir=session_dir,
            headless=False,
            viewport={'width': 1280, 'height': 800},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
        )
        
        page = context.new_page()

        print(f"Navigating to start URL: {start_url}...")
        page.goto(start_url)

        print("Waiting 15 seconds for classroom content to load...")
        time.sleep(15)
        
        # Check if auth required
        if 'auth.udacity.com' in page.url or 'login' in page.url:
            print("Session expired or needed re-auth. Attempting to auto-fill from .env...")
            load_dotenv()
            email = os.getenv("UDACITY_EMAIL")
            password = os.getenv("UDACITY_PASSWORD")
            
            if email and password:
                try:
                    if page.locator("input[type='email']").is_visible(timeout=5000):
                        page.locator("input[type='email']").fill(email)
                    if page.locator("input[type='password']").is_visible():
                        page.locator("input[type='password']").fill(password)
                        
                    # Target the exact 'Sign in' button to strictly avoid 'Sign in with Google/Facebook'
                    button_loc = page.get_by_role("button", name="Sign in", exact=True)
                    if button_loc.is_visible():
                        button_loc.click()
                    else:
                        # Fallback to the last submit button if the exact name differs
                        page.locator("button[type='submit']").last.click()
                except Exception as e:
                    print(f"Could not auto-fill form: {e}")
                    
            print("\n>>> PLEASE CHECK BROWSER WINDOW. IF THERE IS A CAPTCHA OR 2FA, PLEASE SOLVE IT MANUALLY. <<<")
            
            try:
                page.wait_for_url(lambda u: "auth.udacity.com" not in u and "login" not in u, timeout=90000)
            except:
                pass
            
            print("Waiting for login to settle...")
            time.sleep(10)
            
            print("Re-navigating to start URL just in case auth dropped us at the global dashboard...")
            page.goto(start_url)
            time.sleep(15)

        print("Starting syllabus traversal...")
        pages_content = []
        visited_urls = set()
        
        for i in range(50):  # hard cap at 50 to prevent infinite loops
            time.sleep(5) # wait for page navigation and React rendering to stabilize
            current_url = page.url
            if current_url in visited_urls:
                print("We've hit a loop or stuck on the same page. Traversal complete!")
                break
            visited_urls.add(current_url)
            
            print(f"\n--- Scraping Page {i+1} ---")
            
            # Find the main title or heading to label this page
            try:
                title = page.locator("h1, h2").first.inner_text()
            except:
                title = "Unknown Page"
                
            print(f"Title: {title}")
            print(f"URL: {current_url}")
            
            # Get main HTML (fallback to body) to preserve structure and links
            try:
                content = page.locator("body").inner_html()
            except Exception as e:
                print(f"Error extracting html: {e}")
                content = "<p>Error parsing html</p>"
                
            pages_content.append({"title": title, "url": current_url, "content": content})
            
            # Find and click next
            try:
                next_btn = page.locator("button:has-text('Next'), a:has-text('Next'), [aria-label='Next Concept'], [aria-label='Next Lesson']").last
                
                if not next_btn.is_visible():
                    print("No visible 'Next' button found. Finished traversing!")
                    break
                
                print("Attempting to click Next button...")
                navigated = False
                
                # Retry clicking up to 6 times (waiting for React to activate the button)
                for attempt in range(6):
                    next_btn.click(force=True)
                    try:
                        # Wait up to 5 seconds for the URL to change
                        page.wait_for_url(lambda u: u != current_url, timeout=5000)
                        navigated = True
                        print("Navigated successfully!")
                        break
                    except:
                        if attempt < 5:
                            print("Button wasn't ready yet, waiting 3 seconds and retrying...")
                            time.sleep(3)
                            
                if not navigated:
                    print("Could not navigate to next page after multiple attempts. Assuming end of course!")
                    break
                    
            except Exception as e:
                print(f"Could not click 'Next': {e}")
                break
                
        print(f"\nSuccessfully scraped {len(pages_content)} pages.")
        print("Dumping all content to 'capstone_full_content.json'...")
        with open("capstone_full_content.json", "w", encoding="utf-8") as f:
            json.dump(pages_content, f, indent=4)
            
        print("Closing in 5 seconds...")
        time.sleep(5)
        context.close()

if __name__ == "__main__":
    run()
