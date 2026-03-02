#!/usr/bin/env python3
import os
import sys
import json
import requests
from datetime import datetime

# Add root to path for Gold Logger
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from scripts.gold_logger import log_action

VAULT_PATH = "AI_Employee_Vault/Social/Facebook"

class FacebookMCPServer:
    def __init__(self):
        self.page_id = os.getenv("FB_PAGE_ID")
        self.token = os.getenv("FB_ACCESS_TOKEN")

    def _archive(self, action, data):
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(VAULT_PATH, f"{action}_{ts}.json")
        os.makedirs(VAULT_PATH, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        return path

    def post_text(self, message):
        log_action("Gold", "FacebookMCP", "Post Text", "INFO")
        url = f"https://graph.facebook.com/v19.0/{self.page_id}/feed"
        try:
            resp = requests.post(url, data={"message": message, "access_token": self.token})
            res_data = resp.json()
            self._archive("post_text", res_data)
            if resp.status_code == 200:
                log_action("Gold", "FacebookMCP", "Post Text", "SUCCESS", {"id": res_data.get("id")})
                return res_data
            return {"error": res_data}
        except Exception as e:
            log_action("Gold", "FacebookMCP", "Post Text", "ERROR", {"error": str(e)})
            return {"error": str(e)}

    def post_image(self, image_url, caption):
        log_action("Gold", "FacebookMCP", "Post Image", "INFO")
        url = f"https://graph.facebook.com/v19.0/{self.page_id}/photos"
        try:
            resp = requests.post(url, data={"url": image_url, "caption": caption, "access_token": self.token})
            res_data = resp.json()
            self._archive("post_image", res_data)
            if resp.status_code == 200:
                log_action("Gold", "FacebookMCP", "Post Image", "SUCCESS", {"id": res_data.get("id")})
                return res_data
            return {"error": res_data}
        except Exception as e:
            log_action("Gold", "FacebookMCP", "Post Image", "ERROR", {"error": str(e)})
            return {"error": str(e)}

    def fetch_metrics(self):
        log_action("Gold", "FacebookMCP", "Fetch Metrics", "INFO")
        url = f"https://graph.facebook.com/v19.0/{self.page_id}/insights?metric=page_post_engagements,page_impressions&access_token={self.token}"
        try:
            resp = requests.get(url)
            res_data = resp.json()
            self._archive("metrics", res_data)
            log_action("Gold", "FacebookMCP", "Fetch Metrics", "SUCCESS")
            return res_data
        except Exception as e:
            log_action("Gold", "FacebookMCP", "Fetch Metrics", "ERROR", {"error": str(e)})
            return {"error": str(e)}

if __name__ == "__main__":
    fb = FacebookMCPServer()
    if len(sys.argv) > 1:
        if sys.argv[1] == "metrics": print(fb.fetch_metrics())
