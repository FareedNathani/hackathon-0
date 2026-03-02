#!/usr/bin/env python3
import os
import sys
import json
import requests
from datetime import datetime

# Add root to path for Gold Logger
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from scripts.gold_logger import log_action

VAULT_PATH = "AI_Employee_Vault/Social/Instagram"

class InstagramMCPServer:
    def __init__(self):
        self.insta_id = os.getenv("INSTA_ACCOUNT_ID")
        self.token = os.getenv("INSTA_ACCESS_TOKEN")

    def _archive(self, action, data):
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(VAULT_PATH, f"{action}_{ts}.json")
        os.makedirs(VAULT_PATH, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        return path

    def post_image(self, image_url, caption):
        log_action("Gold", "InstagramMCP", "Post Image", "INFO")
        try:
            # 1. Container creation
            create_url = f"https://graph.facebook.com/v19.0/{self.insta_id}/media"
            p1 = {"image_url": image_url, "caption": caption, "access_token": self.token}
            r1 = requests.post(create_url, data=p1).json()
            self._archive("create_container", r1)
            
            if "id" not in r1:
                log_action("Gold", "InstagramMCP", "Post Image", "FAILED", {"step": "container", "error": r1})
                return {"error": r1}
                
            # 2. Publish container
            pub_url = f"https://graph.facebook.com/v19.0/{self.insta_id}/media_publish"
            p2 = {"creation_id": r1["id"], "access_token": self.token}
            r2 = requests.post(pub_url, data=p2).json()
            self._archive("publish", r2)
            
            if "id" in r2:
                log_action("Gold", "InstagramMCP", "Post Image", "SUCCESS", {"id": r2["id"]})
                return r2
            return {"error": r2}
        except Exception as e:
            log_action("Gold", "InstagramMCP", "Post Image", "ERROR", {"error": str(e)})
            return {"error": str(e)}

    def fetch_metrics(self):
        log_action("Gold", "InstagramMCP", "Fetch Metrics", "INFO")
        url = f"https://graph.facebook.com/v19.0/{self.insta_id}/insights?metric=impressions,reach&period=day&access_token={self.token}"
        try:
            resp = requests.get(url)
            res_data = resp.json()
            self._archive("metrics", res_data)
            log_action("Gold", "InstagramMCP", "Fetch Metrics", "SUCCESS")
            return res_data
        except Exception as e:
            log_action("Gold", "InstagramMCP", "Fetch Metrics", "ERROR", {"error": str(e)})
            return {"error": str(e)}

if __name__ == "__main__":
    ig = InstagramMCPServer()
    if len(sys.argv) > 1:
        if sys.argv[1] == "metrics": print(ig.fetch_metrics())
