import time
import os
import sys
import shutil
import subprocess
from pathlib import Path
from dotenv import load_dotenv

# Add root to sys.path
ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(ROOT))
sys.path.append(str(ROOT / "Platinum_AI" / "Shared_Lib"))

from vault_utils import VaultManager
from audit_logger import AuditLogger

# Load Local Secrets
load_dotenv(ROOT / "Platinum_AI" / ".env.local")

AGENT_NAME = os.getenv("AGENT_NAME", "Local_Executive")
VAULT_PATH = os.getenv("VAULT_PATH", "D:/hackathon 0/Vault")
LOG_PATH = os.getenv("LOG_PATH", "D:/hackathon 0/Vault/Logs")

# Skill Path
GMAIL_SKILL = str(ROOT / ".claude" / "skills" / "gmail-send" / "scripts" / "send_email.py")

vault = VaultManager(VAULT_PATH, AGENT_NAME)
logger = AuditLogger(LOG_PATH, AGENT_NAME)

def process_approvals():
    approved_dir = Path(VAULT_PATH) / "Approved"
    if not approved_dir.exists():
        return

    for task_file in approved_dir.glob("*.md"):
        claimed_path = vault.claim_task(task_file)
        if not claimed_path: continue

        logger.log_action("Claim", claimed_path, "SUCCESS", {"source": "Approved"})

        try:
            # EXECUTE REAL GMAIL SKILL
            recipient = "faisalnathani128@gmail.com"
            subject = "Platinum Tier Execution: Final Report"
            body = f"The Platinum Tier AI Employee has successfully processed the task: {task_file.name}. System is 100% operational."
            
            print(f"🚀 [PLATINUM EXEC] Sending real email to {recipient}...")
            result = subprocess.run(["python", GMAIL_SKILL, recipient, subject, body], capture_output=True, text=True)
            
            if result.returncode == 0:
                vault.move_to_done(claimed_path)
                logger.log_action("Execute", claimed_path, "SUCCESS", {"action": "Sent Real Email"})
                update_dashboard(f"SENT REAL EMAIL to {recipient}")
            else:
                print(f"❌ Execution Failed: {result.stderr}")
                logger.log_action("Execute", claimed_path, "FAILED", {"error": result.stderr})

        except Exception as e:
            logger.log_action("Execute", claimed_path, "FAILED", {"error": str(e)})

def update_dashboard(message):
    dash_path = Path(VAULT_PATH) / "Dashboard.md"
    updates_dir = Path(VAULT_PATH) / "Updates"
    pending_updates = ""
    if updates_dir.exists():
        for update in updates_dir.glob("*.md"):
            with open(update, "r", encoding="utf-8") as f:
                pending_updates += f.read() + "\n"
            os.remove(update)

    with open(dash_path, "w", encoding="utf-8") as f:
        f.write("# 👔 Executive Dashboard (Platinum)\n")
        f.write(f"**Last Sync:** {time.ctime()}\n\n")
        f.write("## 📢 Latest Actions\n")
        f.write(f"- {message}\n")
        f.write("\n## ☁️ Cloud Updates\n")
        f.write(pending_updates if pending_updates else "No new cloud signals.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        process_approvals()
        sys.exit(0)
    process_approvals()
