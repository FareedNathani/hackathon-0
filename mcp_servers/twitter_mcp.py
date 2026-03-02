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

VAULT_PATH = "AI_Employee_Vault/Social/Twitter"

class TwitterMCPServer:
    def __init__(self):
        self.consumer_key = os.getenv("X_CONSUMER_KEY")
        self.consumer_secret = os.getenv("X_CONSUMER_SECRET")
        self.access_token = os.getenv("X_ACCESS_TOKEN")
        self.access_token_secret = os.getenv("X_ACCESS_TOKEN_SECRET")

    def _archive(self, action, data):
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(VAULT_PATH, f"{action}_{ts}.json")
        os.makedirs(VAULT_PATH, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        return path

    def post_text(self, text):
        log_action("Gold", "TwitterMCP", "Post Text", "INFO")
        url = "https://api.twitter.com/2/tweets"
        auth = OAuth1(self.consumer_key, self.consumer_secret, self.access_token, self.access_token_secret)
        try:
            resp = requests.post(url, auth=auth, json={"text": text})
            res_data = resp.json()
            self._archive("post_text", res_data)
            if resp.status_code == 201:
                log_action("Gold", "TwitterMCP", "Post Text", "SUCCESS", {"id": res_data.get("data", {}).get("id")})
                return res_data
            return {"error": res_data}
        except Exception as e:
            log_action("Gold", "TwitterMCP", "Post Text", "ERROR", {"error": str(e)})
            return {"error": str(e)}

    def fetch_metrics(self):
        # Twitter v2 API for metrics requires individual tweet IDs or user metrics
        log_action("Gold", "TwitterMCP", "Fetch Metrics", "INFO")
        # Simplified: fetching user metrics
        url = "https://api.twitter.com/2/users/me?user.fields=public_metrics"
        auth = OAuth1(self.consumer_key, self.consumer_secret, self.access_token, self.access_token_secret)
        try:
            resp = requests.get(url, auth=auth)
            res_data = resp.json()
            self._archive("metrics", res_data)
            log_action("Gold", "TwitterMCP", "Fetch Metrics", "SUCCESS")
            return res_data
        except Exception as e:
            log_action("Gold", "TwitterMCP", "Fetch Metrics", "ERROR", {"error": str(e)})
            return {"error": str(e)}

if __name__ == "__main__":
    tw = TwitterMCPServer()
    if len(sys.argv) > 1:
        if sys.argv[1] == "metrics": print(tw.fetch_metrics())
