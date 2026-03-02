#!/usr/bin/env python3
import os
import sys
import json
import requests
from requests_oauthlib import OAuth1
from datetime import datetime

# Add root to path for Gold Logger
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from scripts.gold_logger import log_action

SOCIAL_VAULT = "AI_Employee_Vault/Social"

class SocialMCPServer:
    def __init__(self):
        # Credentials from .env
        self.fb_page_id = os.getenv("FB_PAGE_ID")
        self.fb_token = os.getenv("FB_ACCESS_TOKEN")
        self.insta_id = os.getenv("INSTA_ACCOUNT_ID")
        self.insta_token = os.getenv("INSTA_ACCESS_TOKEN")
        self.x_consumer_key = os.getenv("X_CONSUMER_KEY")
        self.x_consumer_secret = os.getenv("X_CONSUMER_SECRET")
        self.x_access_token = os.getenv("X_ACCESS_TOKEN")
        self.x_access_token_secret = os.getenv("X_ACCESS_TOKEN_SECRET")

    def _archive_response(self, platform, action, response_data):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{platform}_{action}_{timestamp}.json"
        filepath = os.path.join(SOCIAL_VAULT, filename)
        os.makedirs(SOCIAL_VAULT, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(response_data, f, indent=4)
        return filepath

    # --- MCP Tools ---

    def post_to_facebook(self, message):
        """Creates a post on the linked Facebook page."""
        log_action("Gold", "SocialMCP", "Facebook Post Start", "INFO")
        if not all([self.fb_page_id, self.fb_token]):
            error = "Missing Facebook credentials"
            log_action("Gold", "SocialMCP", "Facebook Post", "ERROR", {"error": error})
            return {"error": error}

        url = f"https://graph.facebook.com/v19.0/{self.fb_page_id}/feed"
        try:
            resp = requests.post(url, data={"message": message, "access_token": self.fb_token})
            data = resp.json()
            self._archive_response("facebook", "post", data)
            
            if resp.status_code == 200:
                log_action("Gold", "SocialMCP", "Facebook Post", "SUCCESS", {"id": data.get("id")})
                return {"status": "SUCCESS", "id": data.get("id")}
            else:
                log_action("Gold", "SocialMCP", "Facebook Post", "FAILED", {"error": data})
                return {"status": "FAILED", "error": data}
        except Exception as e:
            log_action("Gold", "SocialMCP", "Facebook Post", "CRITICAL", {"error": str(e)})
            return {"status": "ERROR", "error": str(e)}

    def post_to_x(self, text):
        """Creates a tweet (post) on Twitter/X."""
        log_action("Gold", "SocialMCP", "X Post Start", "INFO")
        if not all([self.x_consumer_key, self.x_consumer_secret, self.x_access_token, self.x_access_token_secret]):
            error = "Missing X credentials"
            log_action("Gold", "SocialMCP", "X Post", "ERROR", {"error": error})
            return {"error": error}

        url = "https://api.twitter.com/2/tweets"
        auth = OAuth1(self.x_consumer_key, self.x_consumer_secret, self.x_access_token, self.x_access_token_secret)
        
        try:
            resp = requests.post(url, auth=auth, json={"text": text})
            data = resp.json()
            self._archive_response("x", "post", data)
            
            if resp.status_code == 201:
                log_action("Gold", "SocialMCP", "X Post", "SUCCESS", {"id": data.get("data", {}).get("id")})
                return {"status": "SUCCESS", "id": data.get("data", {}).get("id")}
            else:
                log_action("Gold", "SocialMCP", "X Post", "FAILED", {"error": data})
                return {"status": "FAILED", "error": data}
        except Exception as e:
            log_action("Gold", "SocialMCP", "X Post", "CRITICAL", {"error": str(e)})
            return {"status": "ERROR", "error": str(e)}

    def post_to_instagram(self, image_url, caption):
        """Creates an Instagram Business post (photo)."""
        log_action("Gold", "SocialMCP", "Instagram Post Start", "INFO")
        if not all([self.insta_id, self.insta_token]):
            error = "Missing Instagram credentials"
            log_action("Gold", "SocialMCP", "Instagram Post", "ERROR", {"error": error})
            return {"error": error}

        try:
            # 1. Container creation
            create_url = f"https://graph.facebook.com/v19.0/{self.insta_id}/media"
            p1 = {"image_url": image_url, "caption": caption, "access_token": self.insta_token}
            r1 = requests.post(create_url, data=p1).json()
            self._archive_response("instagram", "create_container", r1)
            
            if "id" not in r1:
                log_action("Gold", "SocialMCP", "Instagram Post", "FAILED", {"step": "container", "error": r1})
                return {"status": "FAILED", "step": "container", "error": r1}
                
            # 2. Publish container
            pub_url = f"https://graph.facebook.com/v19.0/{self.insta_id}/media_publish"
            p2 = {"creation_id": r1["id"], "access_token": self.insta_token}
            r2 = requests.post(pub_url, data=p2).json()
            self._archive_response("instagram", "publish", r2)
            
            if "id" in r2:
                log_action("Gold", "SocialMCP", "Instagram Post", "SUCCESS", {"id": r2["id"]})
                return {"status": "SUCCESS", "id": r2["id"]}
            else:
                log_action("Gold", "SocialMCP", "Instagram Post", "FAILED", {"step": "publish", "error": r2})
                return {"status": "FAILED", "step": "publish", "error": r2}
        except Exception as e:
            log_action("Gold", "SocialMCP", "Instagram Post", "CRITICAL", {"error": str(e)})
            return {"status": "ERROR", "error": str(e)}

if __name__ == "__main__":
    server = SocialMCPServer()
    if len(sys.argv) > 2:
        platform = sys.argv[1]
        msg = sys.argv[2]
        if platform == "fb": print(server.post_to_facebook(msg))
        elif platform == "x": print(server.post_to_x(msg))
        elif platform == "ig" and len(sys.argv) > 3: print(server.post_to_instagram(msg, sys.argv[3]))
    else:
        print("Social MCP Server Online. Use CLI with [fb/x/ig] and [message] to trigger.")
