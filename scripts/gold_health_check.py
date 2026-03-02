#!/usr/bin/env python3
import os
import sys
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

# Import audit logger
sys.path.append(os.path.dirname(__file__))
from audit_logger import log_event

class GoldHealthCheck:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        self.status = "VALID"
        self.results = {}

    def check_odoo(self):
        url = os.getenv("ODOO_URL")
        db = os.getenv("ODOO_DB")
        username = os.getenv("ODOO_USER")
        password = os.getenv("ODOO_PASSWORD")
        
        if not all([url, db, username, password]):
            self.results["Odoo"] = "MISSING_CONFIG"
            return False

        try:
            auth_url = f"{url}/jsonrpc"
            payload = {
                "jsonrpc": "2.0", "method": "call",
                "params": {"service": "common", "method": "login", "args": [db, username, password]},
                "id": 1
            }
            # Timeout 5s to avoid hanging
            response = requests.post(auth_url, json=payload, timeout=5).json()
            if "result" in response and response["result"]:
                self.results["Odoo"] = "CONNECTED"
                return True
            else:
                self.results["Odoo"] = "AUTH_FAILED"
                return False
        except Exception as e:
            self.results["Odoo"] = f"OFFLINE ({str(e)})"
            return False

    def check_social_apis(self):
        # We'll just check if tokens are configured for now, as full API ping requires valid tokens
        apis = {
            "Facebook": os.getenv("FB_ACCESS_TOKEN"),
            "Instagram": os.getenv("INSTA_ACCESS_TOKEN"),
            "Twitter": os.getenv("X_ACCESS_TOKEN")
        }
        missing = [name for name, val in apis.items() if not val or "your_" in val]
        if missing:
            self.results["SocialAPIs"] = f"MISSING_CONFIG ({', '.join(missing)})"
            return False
        self.results["SocialAPIs"] = "CONFIGURED"
        return True

    def check_logs(self):
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = os.path.join("AI_Employee_Vault", "Logs", f"{today}.json")
        if os.path.exists(log_file):
            self.results["Logs"] = "EXISTS"
            return True
        else:
            self.results["Logs"] = "NOT_FOUND"
            return False

    def check_ceo_briefing(self):
        today = datetime.now().strftime("%Y-%m-%d")
        briefing = os.path.join("vault", "CEO", "Weekly_Briefings", f"CEO_Weekly_Briefing_{today}.md")
        if os.path.exists(briefing):
            self.results["CEOBriefing"] = "GENERATED"
            return True
        else:
            self.results["CEOBriefing"] = "MISSING"
            return False

    def check_ralph_loop(self):
        # We will check if the loop is active by looking for recent log activity
        today_log = os.path.join("AI_Employee_Vault", "Logs", f"{datetime.now().strftime('%Y-%m-%d')}.json")
        if not os.path.exists(today_log):
            self.results["RalphLoop"] = "INACTIVE (No logs)"
            return False
        
        try:
            with open(today_log, "r", encoding="utf-8") as f:
                logs = json.load(f)
                if not logs:
                    self.results["RalphLoop"] = "INACTIVE (Empty logs)"
                    return False
                
                # Check if there's an entry in the last 10 minutes
                last_log = logs[-1]
                last_ts = datetime.fromisoformat(last_log["timestamp"])
                if datetime.now() - last_ts < timedelta(minutes=10):
                    self.results["RalphLoop"] = "ACTIVE"
                    return True
                else:
                    self.results["RalphLoop"] = "STALLED"
                    return False
        except:
            self.results["RalphLoop"] = "ERROR"
            return False

    def run_full_check(self):
        checks = [
            self.check_odoo(),
            self.check_social_apis(),
            self.check_logs(),
            self.check_ceo_briefing(),
            self.check_ralph_loop()
        ]
        
        if all(checks):
            self.status = "VALID"
        else:
            self.status = "INVALID"

        print(f"--- AI Employee Factory Health Check ---")
        for key, result in self.results.items():
            print(f"{key}: {result}")
        print(f"----------------------------------------")
        print(f"Gold Tier Status: {self.status}")
        
        log_event("HealthCheck", "Full Status Check", self.status, self.results)

if __name__ == "__main__":
    from datetime import timedelta
    checker = GoldHealthCheck()
    checker.run_full_check()
