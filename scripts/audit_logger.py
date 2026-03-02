#!/usr/bin/env python3
import os
import json
import shutil
from datetime import datetime

LOG_DIR = "AI_Employee_Vault/Logs"
NEEDS_ACTION = "AI_Employee_Vault/Needs_Action"

def log_event(source, action, status, metadata=None):
    """
    Standardized Audit Logger.
    """
    os.makedirs(LOG_DIR, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = os.path.join(LOG_DIR, f"{today}.json")
    
    event = {
        "timestamp": datetime.now().isoformat(),
        "source": source,
        "action": action,
        "status": status,
        "metadata": metadata or {}
    }
    
    log_data = []
    if os.path.exists(log_file):
        try:
            with open(log_file, "r", encoding="utf-8") as f:
                log_data = json.load(f)
        except:
            log_data = []
            
    log_data.append(event)
    
    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(log_data, f, indent=4)

def handle_failure(source, error_msg, file_path=None):
    """
    Standardized Failure Handler.
    1. Logs the error.
    2. Moves the file to Needs_Action if provided.
    3. Prevents script from crashing by logging and returning.
    """
    log_event(source, "Script Failure", "CRITICAL", {"error": error_msg, "file": file_path})
    
    if file_path and os.path.exists(file_path):
        os.makedirs(NEEDS_ACTION, exist_ok=True)
        dest = os.path.join(NEEDS_ACTION, f"FAILED_{os.path.basename(file_path)}")
        try:
            shutil.move(file_path, dest)
            log_event(source, "Recovery", "SUCCESS", {"action": "File moved to Needs_Action", "dest": dest})
        except Exception as e:
            log_event(source, "Recovery Failed", "ERROR", {"error": str(e)})

if __name__ == "__main__":
    log_event("AuditLogger", "System Init", "SUCCESS")
