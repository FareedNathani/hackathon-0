#!/usr/bin/env python3
import os
import re
import time
import json
import subprocess
import signal
import sys
from datetime import datetime

# Import Audit Logger
from audit_logger import log_event, handle_failure

# --- Configuration ---
VAULT_ROOT = "AI_Employee_Vault"
DIRS = {
    "Inbox": os.path.join(VAULT_ROOT, "Inbox"),
    "Needs_Action": os.path.join(VAULT_ROOT, "Needs_Action"),
    "Needs_Approval": os.path.join(VAULT_ROOT, "Needs_Approval"),
    "Done": os.path.join(VAULT_ROOT, "Done"),
    "Logs": os.path.join(VAULT_ROOT, "Logs")
}

# Skill Scripts
SKILLS = {
    "gmail": os.path.join(".claude", "skills", "gmail-send", "scripts", "send_email.py"),
    "odoo": os.path.join("skills", "odoo-connect", "scripts", "odoo_client.py"),
    "social": os.path.join("skills", "social-poster", "scripts", "post_social.py"),
    "report": os.path.join("skills", "executive-reporter", "scripts", "generate_briefing.py"),
    "audit": os.path.join("skills", "codebase-auditor", "scripts", "audit_code.py")
}

def setup_environment():
    """Ensure all directories exist."""
    try:
        for d in DIRS.values():
            os.makedirs(d, exist_ok=True)
        log_event("RalphLoop", "Environment Setup", "SUCCESS")
    except Exception as e:
        handle_failure("RalphLoopEnv", str(e))

def grace_killer(signum, frame):
    """Handle graceful shutdown."""
    log_event("RalphLoop", "Shutdown", "INITIATED")
    print("\nRalph Wiggum is going to sleep now. Bye bye!")
    sys.exit(0)

signal.signal(signal.SIGINT, grace_killer)
signal.signal(signal.SIGTERM, grace_killer)

class RalphWiggum:
    def __init__(self):
        self.name = "Ralph Wiggum (Autonomous Agent)"
        self.tier = "Gold"

    def run_once(self):
        """Processes one cycle of the factory."""
        self.process_inbox()
        self.execute_pending_tasks()
        self.check_weekly_briefing_trigger()

    def run(self):
        print(f"[{datetime.now()}] I'm helping! (Ralph Wiggum Agent Started)")
        log_event("RalphLoop", "Start", "SUCCESS")
        
        while True:
            try:
                self.run_once()
                time.sleep(10)
            except Exception as e:
                handle_failure("RalphLoop", f"Global Loop Error: {str(e)}")
                time.sleep(30)

    def check_weekly_briefing_trigger(self):
        """Triggers the weekly CEO briefing on Sundays."""
        now = datetime.now()
        if now.weekday() == 6: # Sunday
            today_str = now.strftime("%Y-%m-%d")
            briefing_file = os.path.join("vault", "CEO", "Weekly_Briefings", f"CEO_Weekly_Briefing_{today_str}.md")
            
            if not os.path.exists(briefing_file):
                print(f"[{now}] Sunday Detected! Generating Weekly CEO Briefing...")
                log_event("RalphLoop", "WeeklyBriefingTrigger", "INITIATED")
                
                script_path = os.path.join("scripts", "generate_weekly_ceo_briefing.py")
                if os.path.exists(script_path):
                    subprocess.run(["python", script_path], capture_output=True)
                    log_event("RalphLoop", "WeeklyBriefingTrigger", "SUCCESS")
                else:
                    log_event("RalphLoop", "WeeklyBriefingTrigger", "FAILED", {"error": "Script not found"})

    def process_inbox(self):
        """Move tasks from Inbox to Needs_Action with a plan."""
        try:
            files = [f for f in os.listdir(DIRS["Inbox"]) if f.endswith(".md")]
            
            for filename in files:
                file_path = os.path.join(DIRS["Inbox"], filename)
                log_event("TaskPlanner", "New Task Detected", "SUCCESS", {"file": filename})
                
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    intent = "General"
                    priority = "Medium"
                    needs_approval = "No"
                    
                    lower_content = content.lower()
                    if "urgent" in lower_content: priority = "High"
                    
                    if "odoo" in lower_content: intent = "ERP Integration"
                    elif any(x in lower_content for x in ["facebook", "twitter", "instagram"]):
                        intent = "Social Media"
                        needs_approval = "Yes"
                    elif "report" in lower_content or "briefing" in lower_content: intent = "Reporting"
                    elif "email" in lower_content: 
                        intent = "Communication"
                        needs_approval = "Yes"
                    
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    plan_name = f"Plan_{timestamp}_{filename}"
                    plan_path = os.path.join(DIRS["Needs_Action"], plan_name)
                    
                    plan_content = f"""# Execution Plan\nGenerated: {datetime.now()}\nSource: {filename}\n## Objective\n{content.strip()}\n## Metadata\n- **Intent:** {intent}\n- **Priority:** {priority}\n- **Approval Required:** {needs_approval}\n\n## Action Steps\n1. Validated Intent: {intent}\n2. Execute Skill: [Determine dynamically]\n3. Verify & Archive\n"""
                    with open(plan_path, "w", encoding="utf-8") as f:
                        f.write(plan_content)
                    
                    os.rename(file_path, os.path.join(DIRS["Needs_Action"], f"processed_{filename}"))
                    
                    if needs_approval == "Yes":
                        req_path = os.path.join(DIRS["Needs_Approval"], f"Approval_Request_{filename}")
                        with open(req_path, "w", encoding="utf-8") as f:
                            f.write(f"# Approval Request: {filename}\nAction: {intent}\nStatus: PENDING\nInstructions: Add 'APPROVED' to proceed.")
                        log_event("TaskPlanner", "Approval Request Created", "SUCCESS", {"file": filename})

                    log_event("TaskPlanner", "Plan Created", "SUCCESS", {"plan": plan_name})
                    
                except Exception as e:
                    handle_failure("TaskPlanner", str(e), file_path)
        except Exception as e:
            log_event("TaskPlanner", "Directory Scan Error", "ERROR", {"error": str(e)})

    def execute_pending_tasks(self):
        """Execute plans in Needs_Action."""
        try:
            plans = [f for f in os.listdir(DIRS["Needs_Action"]) if f.startswith("Plan_") and f.endswith(".md")]
            
            for plan_file in plans:
                plan_path = os.path.join(DIRS["Needs_Action"], plan_file)
                
                try:
                    with open(plan_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    
                    if "Approval Required: Yes" in content:
                        source_match = re.search(r"Source: (.*?)\n", content)
                        if source_match:
                            source_name = source_match.group(1).strip()
                            if not self.check_approval(source_name):
                                continue 

                    log_event("Executor", "Execution Start", "PROCESSING", {"plan": plan_file})
                    
                    lower_content = content.lower()
                    success = False
                    
                    if "erp integration" in lower_content:
                        subprocess.run(["python", SKILLS["odoo"]], capture_output=True)
                        log_event("SkillExecution", "Odoo Skill Call", "SUCCESS")
                        success = True
                    elif "social media" in lower_content:
                        subprocess.run(["python", SKILLS["social"]], capture_output=True)
                        log_event("SkillExecution", "Social Poster Skill Call", "SUCCESS")
                        success = True
                    elif "reporting" in lower_content:
                        subprocess.run(["python", SKILLS["report"]], capture_output=True)
                        log_event("SkillExecution", "Executive Reporter Skill Call", "SUCCESS")
                        success = True
                    elif "communication" in lower_content:
                        # Call actual Gmail skill
                        subject = "Gold Tier AI Employee Notification"
                        body = f"Objective: {content.strip()}"
                        recipient = "faisalnathani128@gmail.com"
                        
                        log_event("SkillExecution", "Gmail Skill Call", "INITIATED", {"recipient": recipient})
                        result = subprocess.run(["python", SKILLS["gmail"], recipient, subject, body], capture_output=True, text=True)
                        
                        if result.returncode == 0:
                            log_event("SkillExecution", "Gmail Skill Call", "SUCCESS")
                            success = True
                        else:
                            handle_failure("GmailSkill", result.stderr or "Unknown Error")
                            success = False
                    else:
                        log_event("Executor", "Skill Match", "SKIPPED", {"reason": "No matching skill"})
                        success = True

                    if success:
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
                        done_path = os.path.join(DIRS["Done"], f"Completed_{timestamp}_{plan_file}")
                        os.rename(plan_path, done_path)
                        
                        source_match = re.search(r"Source: (.*?)\n", content)
                        if source_match:
                            source_name = source_match.group(1).strip()
                            processed_source = os.path.join(DIRS["Needs_Action"], f"processed_{source_name}")
                            if os.path.exists(processed_source):
                                os.rename(processed_source, os.path.join(DIRS["Done"], f"Source_{source_name}"))

                        log_event("Executor", "Task Complete", "SUCCESS", {"plan": plan_file})

                except Exception as e:
                    handle_failure("Executor", str(e), plan_path)
        except Exception as e:
            log_event("Executor", "Directory Scan Error", "ERROR", {"error": str(e)})

    def check_approval(self, source_filename):
        """Check Needs_Approval folder."""
        if not os.path.exists(DIRS["Needs_Approval"]): return False
        for f in os.listdir(DIRS["Needs_Approval"]):
            if source_filename in f:
                path = os.path.join(DIRS["Needs_Approval"], f)
                with open(path, "r", encoding="utf-8") as approval_file:
                    if "APPROVED" in approval_file.read().upper():
                        log_event("Approval", "Check", "GRANTED", {"file": source_filename})
                        return True
        return False

if __name__ == "__main__":
    setup_environment()
    ralph = RalphWiggum()
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        ralph.run_once()
    else:
        ralph.run()
