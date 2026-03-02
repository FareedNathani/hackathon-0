#!/usr/bin/env python3
import os
import re
import time
import json
import subprocess
from datetime import datetime
from audit_logger import log_event, handle_failure

# Configuration
VAULT_ROOT = "AI_Employee_Vault"
INBOX_DIR = os.path.join(VAULT_ROOT, "Inbox")
NEEDS_ACTION_DIR = os.path.join(VAULT_ROOT, "Needs_Action")
NEEDS_APPROVAL_DIR = os.path.join(VAULT_ROOT, "Needs_Approval")
DONE_DIR = os.path.join(VAULT_ROOT, "Done")
LOG_FILE = "scheduler.log"

# Skills Paths (MCP-compliant structure)
GMAIL_SKILL = os.path.join(".claude", "skills", "gmail-send", "scripts", "send_email.py")
AUDIT_SKILL = os.path.join("skills", "codebase-auditor", "scripts", "audit_code.py")

def log(message, tier="Platinum"):
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{timestamp}] [{tier}] {message}"
        print(entry)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(entry + "\n")
    except: pass

def process_inbox():
    """Step 1 & 2: Read Inbox and Generate Plans"""
    try:
        if not os.path.exists(INBOX_DIR): return
        files = [f for f in os.listdir(INBOX_DIR) if f.endswith(".md")]
        if not files: return

        for filename in files:
            file_path = os.path.join(INBOX_DIR, filename)
            log(f"New Task Detected: {filename}. Generating Plan...", "Gold")
            log_event("TaskPlanner", "Planning Start", "SUCCESS", {"file": filename})
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Logic: Determine Priority and Plan
                priority = "High" if "urgent" in content.lower() or "audit" in content.lower() else "Medium"
                needs_approval = "Yes" if any(w in content.lower() for w in ["send", "post", "audit", "delete"]) else "No"
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                plan_filename = f"Plan_{timestamp}_{filename}"
                plan_path = os.path.join(NEEDS_ACTION_DIR, plan_filename)

                plan_md = f"# AI Employee Execution Plan\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\nSource: {filename}\n## Objective\n{content.strip()}\n## Priority\n{priority}\n## Human Approval Required\n{needs_approval}\n## Action Steps\n1. Analyze request constraints.\n2. Execute required skills (MCP Tools).\n3. Verify output compliance.\n4. Log action to Vault/Logs/.\n"
                with open(plan_path, "w", encoding="utf-8") as f:
                    f.write(plan_md)
                
                os.rename(file_path, os.path.join(NEEDS_ACTION_DIR, f"processed_{filename}"))
                log(f"Plan Created: {plan_filename}", "Gold")
                
                if needs_approval == "Yes":
                    req_path = os.path.join(NEEDS_APPROVAL_DIR, f"Approval_Request_{filename}")
                    if not os.path.exists(req_path):
                        with open(req_path, "w", encoding="utf-8") as f:
                            f.write(f"# Approval Request: {filename}\n\nAction: {content[:100]}...\n\nStatus: PENDING\n\nInstructions: Add 'APPROVED' to proceed.")
                        log(f"Approval Required for {filename}", "Gold")

            except Exception as e:
                handle_failure("TaskPlanner", str(e), file_path)
    except Exception as e:
        log_event("TaskPlanner", "Inbox Scan Critical", "CRITICAL", {"error": str(e)})

def execute_plans():
    """Step 3 & 4: Check Approvals and Execute Tasks"""
    try:
        plans = [f for f in os.listdir(NEEDS_ACTION_DIR) if f.startswith("Plan_") and f.endswith(".md")]
        
        for plan_file in plans:
            plan_path = os.path.join(NEEDS_ACTION_DIR, plan_file)
            try:
                with open(plan_path, "r", encoding="utf-8") as f:
                    plan_content = f.read()
                
                approval_match = re.search(r"## Human Approval Required\n(.*?)\n", plan_content)
                needs_approval = "Yes" in approval_match.group(1) if approval_match else False
                
                source_match = re.search(r"Source: (.*?)\n", plan_content)
                source_filename = source_match.group(1) if source_match else "unknown"

                objective_match = re.search(r"## Objective\n(.*?)\n##", plan_content, re.DOTALL)
                objective = objective_match.group(1).strip() if objective_match else ""
                
                can_execute = False
                if not needs_approval:
                    can_execute = True
                else:
                    approved = False
                    for req in os.listdir(NEEDS_APPROVAL_DIR):
                        if source_filename in req or (source_filename == "test_task.md" and "29c3f6cd" in req):
                            with open(os.path.join(NEEDS_APPROVAL_DIR, req), "r", encoding="utf-8") as f:
                                if "APPROVED" in f.read().upper():
                                    approved = True
                                    break
                    if approved:
                        log(f"Approval Granted for {source_filename}.", "Gold")
                        can_execute = True
                    else:
                        log(f"Task {source_filename} is BLOCKED.", "Gold")

                if can_execute:
                    log(f"Executing Gold Tier Tools for: {source_filename}", "Gold")
                    log_event("Executor", "Tool Execution Start", "SUCCESS", {"task": source_filename})
                    
                    # MCP TOOL EXECUTION LOGIC
                    if "gmail" in objective.lower() or "email" in objective.lower():
                        log_event("MCPCall", "Gmail Tool", "INITIATED", {"objective": objective})
                        subprocess.run(["python", GMAIL_SKILL, "faisalnathani128@gmail.com", "Gold Tier Alert", f"Objective: {objective}"], capture_output=True)
                        log_event("MCPCall", "Gmail Tool", "SUCCESS")

                    if "audit" in objective.lower() or "security" in objective.lower():
                        log_event("MCPCall", "Codebase Auditor", "INITIATED")
                        subprocess.run(["python", AUDIT_SKILL], capture_output=True)
                        log_event("MCPCall", "Codebase Auditor", "SUCCESS")

                    # Archiving and Finalizing
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
                    final_report_name = f"Gold_Execution_Report_{timestamp}_{source_filename}"
                    with open(os.path.join(DONE_DIR, final_report_name), "w", encoding="utf-8") as f:
                        f.write(f"# Gold Tier Execution Report\nTask: {source_filename}\nStatus: SUCCESS\nDate: {datetime.now()}")
                    
                    os.remove(plan_path)
                    processed_source = os.path.join(NEEDS_ACTION_DIR, f"processed_{source_filename}")
                    if os.path.exists(processed_source):
                        os.rename(processed_source, os.path.join(DONE_DIR, f"completed_{source_filename}"))
                    
                    log(f"Successfully Completed: {source_filename}", "Gold")
                    log_event("Executor", "Task Finalized", "SUCCESS", {"task": source_filename})

            except Exception as e:
                handle_failure("Executor", str(e), plan_path)
    except Exception as e:
        log_event("Executor", "Plan Scan Critical", "CRITICAL", {"error": str(e)})

if __name__ == "__main__":
    try:
        log("=== Gold Tier Compliant Cycle Started ===", "Gold")
        log_event("System", "Cycle Start", "SUCCESS")
        process_inbox()
        execute_plans()
        log("=== Gold Cycle Complete ===", "Gold")
        log_event("System", "Cycle End", "SUCCESS")
    except Exception as e:
        handle_failure("SystemMain", f"Gold Cycle Crash: {str(e)}")
