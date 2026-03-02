#!/usr/bin/env python3
import os
import json
import requests
import sys
from datetime import datetime

# Add root scripts to path for Gold Logger
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../scripts')))
from gold_logger import log_action

class OdooClient:
    def __init__(self):
        self.url = os.getenv("ODOO_URL")
        self.db = os.getenv("ODOO_DB")
        self.username = os.getenv("ODOO_USER")
        self.password = os.getenv("ODOO_PASSWORD")
        self.uid = None

    def authenticate(self):
        if not all([self.url, self.db, self.username, self.password]):
            log_action("Gold", "OdooConnect", "Init", "ERROR", {"error": "Missing Odoo credentials"})
            raise ValueError("Missing Odoo credentials in .env")

        try:
            # Common authentication endpoint
            auth_url = f"{self.url}/jsonrpc"
            payload = {
                "jsonrpc": "2.0",
                "method": "call",
                "params": {
                    "service": "common",
                    "method": "login",
                    "args": [self.db, self.username, self.password]
                },
                "id": 1
            }
            response = requests.post(auth_url, json=payload).json()
            
            if "result" in response and response["result"]:
                self.uid = response["result"]
                log_action("Gold", "OdooConnect", "Auth", "SUCCESS", {"uid": self.uid})
                return True
            else:
                log_action("Gold", "OdooConnect", "Auth", "FAILED", {"response": response})
                return False

        except Exception as e:
            log_action("Gold", "OdooConnect", "Auth", "CRITICAL", {"error": str(e)})
            return False

    def execute_kw(self, model, method, args=None, kwargs=None):
        if not self.uid and not self.authenticate():
            return None

        url = f"{self.url}/jsonrpc"
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "service": "object",
                "method": "execute_kw",
                "args": [self.db, self.uid, self.password, model, method, args or []],
                "kwargs": kwargs or {}
            },
            "id": 2
        }
        
        try:
            response = requests.post(url, json=payload).json()
            if "result" in response:
                log_action("Gold", "OdooConnect", f"Execute: {model}.{method}", "SUCCESS")
                return response["result"]
            else:
                error = response.get("error", {}).get("data", {}).get("message", "Unknown Error")
                log_action("Gold", "OdooConnect", f"Execute: {model}.{method}", "ERROR", {"error": error})
                return None
        except Exception as e:
            log_action("Gold", "OdooConnect", f"Execute: {model}.{method}", "CRITICAL", {"error": str(e)})
            return None

if __name__ == "__main__":
    # Test execution
    client = OdooClient()
    # Attempt to read partners (customers)
    partners = client.execute_kw('res.partner', 'search_read', [[['is_company', '=', True]]], {'fields': ['name', 'country_id'], 'limit': 5})
    if partners:
        print(f"Found {len(partners)} partners.")
    else:
        print("Odoo connection test failed or no data.")
