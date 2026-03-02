#!/usr/bin/env python3
import os
import sys
import time
import subprocess
from datetime import datetime

# Configuration
VAULT_ROOT = "AI_Employee_Vault"
INBOX_DIR = os.path.join(VAULT_ROOT, "Inbox")
NEEDS_ACTION_DIR = os.path.join(VAULT_ROOT, "Needs_Action")
LOG_FILE = "scheduler.log"

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] {message}"
    print(entry)
    with open(LOG_FILE, "a") as f:
        f.write(entry + "\n")

def process_inbox():
    """Checks Inbox and processes each task file."""
    if not os.path.exists(INBOX_DIR):
        log(f"Error: Inbox directory {INBOX_DIR} not found.")
        return

    files = [f for f in os.listdir(INBOX_DIR) if f.endswith(".md")]
    
    if not files:
        log("Inbox is empty. No tasks to process.")
        return

    log(f"Found {len(files)} task(s) in Inbox. Starting Task Planner...")

    for filename in files:
        file_path = os.path.join(INBOX_DIR, filename)
        log(f"Processing: {filename}")
        
        # Simulate running the task-planner skill logic
        # (Since task-planner is a procedural skill, we implement its logic here 
        # to ensure production-level reliability in this automated script)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                task_content = f.read()

            # Logic: Determine Priority and Plan
            priority = "High" if "urgent" in task_content.lower() or "asap" in task_content.lower() else "Medium"
            needs_approval = "Yes" if any(word in task_content.lower() for word in ["delete", "send", "payment", "post"]) else "No"
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            plan_filename = f"Plan_{timestamp}_{filename}"
            plan_path = os.path.join(NEEDS_ACTION_DIR, plan_filename)

            plan_md = f"""# AI Employee Execution Plan
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Source: {filename}

## Objective
{task_content.strip()}

## Priority
{priority}

## Human Approval Required
{needs_approval}

## Action Steps
1. Analyze request constraints.
2. Execute required skills (Gmail/LinkedIn/Vault).
3. Verify output.
4. Move source to Done.
"""
            # Ensure Needs_Action exists
            os.makedirs(NEEDS_ACTION_DIR, exist_ok=True)
            
            with open(plan_path, "w", encoding="utf-8") as f:
                f.write(plan_md)

            # Move processed task to avoid re-processing
            # Using our vault-file-manager skill logic
            processed_filename = f"processed_{filename}"
            processed_path = os.path.join(NEEDS_ACTION_DIR, processed_filename)
            os.rename(file_path, processed_path)
            
            log(f"Success: Created {plan_filename} and moved source to Needs_Action.")

        except Exception as e:
            log(f"Error processing {filename}: {str(e)}")

if __name__ == "__main__":
    log("=== AI Employee Scheduler Started ===")
    process_inbox()
    log("=== Scheduler Run Complete ===")
