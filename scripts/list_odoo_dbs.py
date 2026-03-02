#!/usr/bin/env python3
import os
import requests
from dotenv import load_dotenv

def list_odoo_databases():
    load_dotenv()
    url = os.getenv("ODOO_URL")
    if not url:
        print("ODOO_URL not found in .env")
        return

    json_url = f"{url}/jsonrpc"
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "db",
            "method": "list",
            "args": []
        },
        "id": 1
    }
    
    try:
        response = requests.post(json_url, json=payload).json()
        if "result" in response:
            print("Available Odoo Databases:")
            for db in response["result"]:
                print(f"- {db}")
        else:
            print("Could not list databases. Result: {}".format(response))
    except Exception as e:
        print(f"Error connecting to Odoo: {e}")

if __name__ == "__main__":
    list_odoo_databases()
