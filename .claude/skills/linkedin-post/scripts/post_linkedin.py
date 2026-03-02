#!/usr/bin/env python3
import os
import sys
import argparse
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def post_to_linkedin(content):
    email = os.environ.get('LINKEDIN_EMAIL')
    password = os.environ.get('LINKEDIN_PASSWORD')

    if not email or not password:
        print("Error: LINKEDIN_EMAIL or LINKEDIN_PASSWORD environment variables not set.")
        sys.exit(1)

    try:
        with sync_playwright() as p:
            # Using chromium in non-headless mode to allow human interaction
            browser = p.chromium.launch(headless=False)
            context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
            page = context.new_page()
            
            # Login Process
            page.goto("https://www.linkedin.com/login", wait_until="networkidle")
            page.fill("#username", email)
            page.fill("#password", password)
            page.click("button[type='submit']")
            
            # Ensure feed is reached (check for common feed selectors)
            try:
                # Wait up to 120 seconds to allow for manual 2FA/CAPTCHA completion
                print("Waiting for login success... Please complete any 2FA/CAPTCHA in the browser window.")
                page.wait_for_selector(".share-box-feed-entry__trigger", timeout=120000)
            except Exception:
                # Potential 2FA or failed login check
                if "checkpoint" in page.url:
                    print("Error: LinkedIn 2FA challenge detected. Automation blocked.")
                else:
                    print("Error: Login failed or feed timeout. Verify credentials.")
                browser.close()
                sys.exit(1)

            # Start Post Creation
            page.click(".share-box-feed-entry__trigger")
            
            # Wait for editor to appear
            page.wait_for_selector(".ql-editor", timeout=5000)
            page.fill(".ql-editor", content)
            
            # Click Post button (primary action in share box)
            page.click(".share-actions__primary-action")
            
            # Wait for modal to close (success indicator)
            page.wait_for_selector(".share-box-feed-entry__trigger", state="visible", timeout=10000)
            
            browser.close()
            print("Success: LinkedIn post created.")

    except Exception as e:
        print(f"Error: Failed to post to LinkedIn. {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automated LinkedIn post creator.")
    parser.add_argument("content", help="The text content for your LinkedIn post.")
    
    args = parser.parse_args()
    post_to_linkedin(args.content)
