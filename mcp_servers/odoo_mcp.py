#!/usr/bin/env python3
import os
import sys
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

# Add root scripts to path for Gold Logger
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts')))
from gold_logger import log_action

# Configuration
ACCOUNTING_VAULT = "AI_Employee_Vault/Accounting"

class OdooMCPServer:
    def __init__(self):
        # Explicitly load .env from the root directory
        env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../.env'))
        load_dotenv(env_path)
        
        self.url = os.getenv("ODOO_URL")
        self.db = os.getenv("ODOO_DB")
        self.username = os.getenv("ODOO_USER")
        self.password = os.getenv("ODOO_PASSWORD")
        self.uid = None

    def authenticate(self):
        if not all([self.url, self.db, self.username, self.password]):
            log_action("Gold", "OdooMCP", "Init", "ERROR", {"error": "Missing Odoo credentials in .env"})
            return False

        try:
            auth_url = f"{self.url}/jsonrpc"
            payload = {
                "jsonrpc": "2.0", "method": "call",
                "params": {"service": "common", "method": "login", "args": [self.db, self.username, self.password]},
                "id": 1
            }
            raw_response = requests.post(auth_url, json=payload)
            try:
                response = raw_response.json()
            except json.JSONDecodeError:
                log_action("Gold", "OdooMCP", "Auth", "CRITICAL", {"error": "Invalid JSON Response", "raw": raw_response.text[:500]})
                return False

            if "result" in response and response["result"]:
                self.uid = response["result"]
                log_action("Gold", "OdooMCP", "Auth", "SUCCESS", {"uid": self.uid})
                return True
            else:
                log_action("Gold", "OdooMCP", "Auth", "FAILED", {"response": response})
                return False
        except Exception as e:
            log_action("Gold", "OdooMCP", "Auth", "CRITICAL", {"error": str(e)})
            return False

    def call_odoo(self, model, method, args=None, kwargs=None):
        if not self.uid and not self.authenticate():
            return {"error": "Authentication failed"}

        log_action("Gold", "OdooMCP", f"Request: {model}.{method}", "INFO", {"args": args, "kwargs": kwargs})
        
        url = f"{self.url}/jsonrpc"
        payload = {
            "jsonrpc": "2.0", "method": "call",
            "params": {
                "service": "object", "method": "execute_kw",
                "args": [self.db, self.uid, self.password, model, method, args or []],
                "kwargs": kwargs or {}
            },
            "id": 2
        }
        
        try:
            response = requests.post(url, json=payload).json()
            if "result" in response:
                result = response["result"]
                log_action("Gold", "OdooMCP", f"Response: {model}.{method}", "SUCCESS")
                self.save_to_vault(model, method, result)
                return result
            else:
                error = response.get("error", {}).get("data", {}).get("message", "Unknown Error")
                log_action("Gold", "OdooMCP", f"Error: {model}.{method}", "ERROR", {"error": error})
                return {"error": error}
        except Exception as e:
            log_action("Gold", "OdooMCP", f"CriticalError: {model}.{method}", "CRITICAL", {"error": str(e)})
            return {"error": str(e)}

    def save_to_vault(self, model, method, data):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{model}_{method}_{timestamp}.json"
        filepath = os.path.join(ACCOUNTING_VAULT, filename)
        os.makedirs(ACCOUNTING_VAULT, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        print(f"Data saved to: {filepath}")

    # --- MCP Tools ---

    def read_sales_orders(self):
        """Read latest 10 sales orders."""
        return self.call_odoo('sale.order', 'search_read', [], {'fields': ['name', 'partner_id', 'amount_total', 'state'], 'limit': 10})

    def read_invoices(self):
        """Read latest 10 customer invoices."""
        return self.call_odoo('account.move', 'search_read', [[['move_type', '=', 'out_invoice']]], {'fields': ['name', 'partner_id', 'amount_total', 'state', 'invoice_date'], 'limit': 10})

    def read_payments(self):
        """Read latest 10 payments."""
        return self.call_odoo('account.payment', 'search_read', [], {'fields': ['name', 'partner_id', 'amount', 'state', 'date'], 'limit': 10})

    def create_customer(self, name, email=None):
        """Create a new customer record."""
        vals = {'name': name, 'email': email, 'is_company': True}
        return self.call_odoo('res.partner', 'create', [vals])

    def create_draft_invoice(self, partner_id, lines):
        """
        Create a draft customer invoice.
        lines: list of dicts with product_id, quantity, price_unit
        """
        invoice_lines = []
        for line in lines:
            invoice_lines.append((0, 0, {
                'product_id': line['product_id'],
                'quantity': line['quantity'],
                'price_unit': line['price_unit'],
                'name': 'Draft Invoice Line'
            }))
            
        vals = {
            'move_type': 'out_invoice',
            'partner_id': partner_id,
            'invoice_line_ids': invoice_lines
        }
        return self.call_odoo('account.move', 'create', [vals])

if __name__ == "__main__":
    server = OdooMCPServer()
    # Simple CLI interface for manual trigger
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "read_sales": print(server.read_sales_orders())
        elif cmd == "read_invoices": print(server.read_invoices())
        elif cmd == "read_payments": print(server.read_payments())
        elif cmd == "create_customer":
            if len(sys.argv) > 2: print(server.create_customer(sys.argv[2]))
            else: print("Provide customer name.")
    else:
        print("Odoo MCP Server Online. Use CLI commands like 'read_sales' to trigger.")
