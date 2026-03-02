#!/usr/bin/env python3
import os
import sys
import json
from datetime import datetime

# Add mcp_servers to path to import OdooMCPServer
sys.path.append(os.path.abspath('mcp_servers'))
from odoo_mcp import OdooMCPServer

def run_comprehensive_odoo_test():
    print(f"--- Odoo Comprehensive Test Started [{datetime.now()}] ---")
    server = OdooMCPServer()
    
    # 1. Test Authentication
    print("[1/5] Testing Authentication...")
    if server.authenticate():
        print("✅ Authentication Successful (UID: {})".format(server.uid))
    else:
        print("❌ Authentication Failed. Check credentials in .env")
        return

    # 2. Test Sales Orders
    print("[2/5] Fetching Sales Orders...")
    sales = server.read_sales_orders()
    if isinstance(sales, list):
        print("✅ Found {} sales orders.".format(len(sales)))
        if sales:
            print("   Sample Order: {} (Total: {})".format(sales[0].get('name'), sales[0].get('amount_total')))
    else:
        print("❌ Error fetching sales: {}".format(sales))

    # 3. Test Invoices
    print("[3/5] Fetching Invoices...")
    invoices = server.read_invoices()
    if isinstance(invoices, list):
        print("✅ Found {} invoices.".format(len(invoices)))
    else:
        print("❌ Error fetching invoices: {}".format(invoices))

    # 4. Test Payments
    print("[4/5] Fetching Payments...")
    payments = server.read_payments()
    if isinstance(payments, list):
        print("✅ Found {} payments.".format(len(payments)))
    else:
        print("❌ Error fetching payments: {}".format(payments))

    # 5. Test Customer Search
    print("[5/5] Searching for Companies...")
    partners = server.call_odoo('res.partner', 'search_read', [[['is_company', '=', True]]], {'fields': ['name'], 'limit': 5})
    if isinstance(partners, list):
        print("✅ Found {} companies.".format(len(partners)))
        for p in partners:
            print("   - {}".format(p.get('name')))
    else:
        print("❌ Error fetching partners: {}".format(partners))

    print("--- Test Complete ---")

if __name__ == "__main__":
    run_comprehensive_odoo_test()
