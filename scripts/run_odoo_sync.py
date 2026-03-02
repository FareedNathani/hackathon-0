#!/usr/bin/env python3
import os
import sys
from datetime import datetime

# Add root to path to import mcp_servers and gold_logger
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from mcp_servers.odoo_mcp import OdooMCPServer
from scripts.gold_logger import log_action

def run_daily_sync():
    """
    Performs a full synchronization of Odoo data to the Accounting Vault.
    Designed for daily execution via scheduler.
    """
    log_action("Gold", "OdooSync", "Daily Sync Start", "SUCCESS")
    print(f"[{datetime.now()}] Starting Odoo Daily Sync...")
    
    server = OdooMCPServer()
    
    try:
        # 1. Sync Sales Orders
        print("Syncing Sales Orders...")
        sales = server.read_sales_orders()
        if isinstance(sales, list):
            log_action("Gold", "OdooSync", "Sync Sales Orders", "SUCCESS", {"count": len(sales)})
        
        # 2. Sync Invoices
        print("Syncing Invoices...")
        invoices = server.read_invoices()
        if isinstance(invoices, list):
            log_action("Gold", "OdooSync", "Sync Invoices", "SUCCESS", {"count": len(invoices)})
            
        # 3. Sync Payments
        print("Syncing Payments...")
        payments = server.read_payments()
        if isinstance(payments, list):
            log_action("Gold", "OdooSync", "Sync Payments", "SUCCESS", {"count": len(payments)})
            
        log_action("Gold", "OdooSync", "Daily Sync Complete", "SUCCESS")
        print(f"[{datetime.now()}] Odoo Daily Sync Finished Successfully.")
        
    except Exception as e:
        log_action("Gold", "OdooSync", "Daily Sync Failed", "CRITICAL", {"error": str(e)})
        print(f"Error during sync: {e}")

if __name__ == "__main__":
    run_daily_sync()
