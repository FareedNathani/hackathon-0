#!/usr/bin/env python3
import os
import sys
import json
import requests
from requests_oauthlib import OAuth1

# Add root scripts to path for Gold Logger
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../scripts')))
from gold_logger import log_action

class SocialPoster:
    def __init__(self):
        self.fb_token = os.getenv("FB_ACCESS_TOKEN")
        self.fb_page_id = os.getenv("FB_PAGE_ID")
        
        self.insta_id = os.getenv("INSTA_ACCOUNT_ID")
        self.insta_token = os.getenv("INSTA_ACCESS_TOKEN")
        
        self.x_consumer_key = os.getenv("X_CONSUMER_KEY")
        self.x_consumer_secret = os.getenv("X_CONSUMER_SECRET")
        self.x_access_token = os.getenv("X_ACCESS_TOKEN")
        self.x_access_token_secret = os.getenv("X_ACCESS_TOKEN_SECRET")

    def post_facebook(self, message):
        if not self.fb_token or not self.fb_page_id:
            log_action("Gold", "SocialPoster", "Facebook", "SKIPPED", {"reason": "Missing credentials"})
            return False

        url = f"https://graph.facebook.com/v19.0/{self.fb_page_id}/feed"
        try:
            resp = requests.post(url, data={"message": message, "access_token": self.fb_token})
            if resp.status_code == 200:
                log_action("Gold", "SocialPoster", "Facebook", "SUCCESS", {"id": resp.json().get("id")})
                return True
            else:
                log_action("Gold", "SocialPoster", "Facebook", "FAILED", {"error": resp.text})
                return False
        except Exception as e:
            log_action("Gold", "SocialPoster", "Facebook", "ERROR", {"error": str(e)})
            return False

    def post_instagram(self, image_url, caption):
        """Instagram requires an image container creation flow."""
        if not self.insta_id or not self.insta_token:
            log_action("Gold", "SocialPoster", "Instagram", "SKIPPED", {"reason": "Missing credentials"})
            return False

        base_url = f"https://graph.facebook.com/v19.0/{self.insta_id}"
        
        try:
            # 1. Create Media Container
            create_url = f"{base_url}/media"
            payload = {
                "image_url": image_url,
                "caption": caption,
                "access_token": self.insta_token
            }
            container_resp = requests.post(create_url, data=payload).json()
            
            if "id" not in container_resp:
                log_action("Gold", "SocialPoster", "Instagram", "FAILED", {"step": "container", "error": container_resp})
                return False
                
            creation_id = container_resp["id"]
            
            # 2. Publish Container
            publish_url = f"{base_url}/media_publish"
            publish_payload = {
                "creation_id": creation_id,
                "access_token": self.insta_token
            }
            pub_resp = requests.post(publish_url, data=publish_payload)
            
            if pub_resp.status_code == 200:
                log_action("Gold", "SocialPoster", "Instagram", "SUCCESS", {"id": pub_resp.json().get("id")})
                return True
            else:
                log_action("Gold", "SocialPoster", "Instagram", "FAILED", {"step": "publish", "error": pub_resp.text})
                return False
                
        except Exception as e:
            log_action("Gold", "SocialPoster", "Instagram", "ERROR", {"error": str(e)})
            return False

    def post_twitter(self, text):
        if not all([self.x_consumer_key, self.x_consumer_secret, self.x_access_token, self.x_access_token_secret]):
            log_action("Gold", "SocialPoster", "Twitter", "SKIPPED", {"reason": "Missing credentials"})
            return False

        url = "https://api.twitter.com/2/tweets"
        auth = OAuth1(self.x_consumer_key, self.x_consumer_secret, self.x_access_token, self.x_access_token_secret)
        
        try:
            resp = requests.post(url, auth=auth, json={"text": text})
            if resp.status_code == 201:
                log_action("Gold", "SocialPoster", "Twitter", "SUCCESS", {"id": resp.json().get("data", {}).get("id")})
                return True
            else:
                log_action("Gold", "SocialPoster", "Twitter", "FAILED", {"error": resp.text})
                return False
        except Exception as e:
            log_action("Gold", "SocialPoster", "Twitter", "ERROR", {"error": str(e)})
            return False

if __name__ == "__main__":
    poster = SocialPoster()
    # Example usage (will fail without real creds, but logs attempt)
    poster.post_twitter("Hello World from AI Employee Factory!")
