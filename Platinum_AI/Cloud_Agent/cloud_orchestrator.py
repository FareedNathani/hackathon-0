import time
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add root to sys.path to find Shared_Lib
ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(ROOT))

try:
    # Add Shared_Lib specifically
    sys.path.append(str(ROOT / "Platinum_AI" / "Shared_Lib"))
    from vault_utils import VaultManager
    from audit_logger import AuditLogger
except Exception as e:
    with open(str(ROOT / "cloud_agent_error.log"), "a") as f:
        f.write(f"Import Error: {e}\n")
    sys.exit(1)

# Load Secrets
load_dotenv(ROOT / "Platinum_AI" / ".env.cloud")

AGENT_NAME = os.getenv("AGENT_NAME", "Cloud_Worker")
VAULT_PATH = os.getenv("VAULT_PATH", "./Vault")
LOG_PATH = os.getenv("LOG_PATH", "./Vault/Logs")

vault = VaultManager(VAULT_PATH, AGENT_NAME)
logger = AuditLogger(LOG_PATH, AGENT_NAME)

def process_needs_action():
    """Scans Needs_Action/email/ and claims tasks."""
    email_tasks_dir = Path(VAULT_PATH) / "Needs_Action" / "email"
    if not email_tasks_dir.exists():
        return

    for task_file in email_tasks_dir.glob("*.md"):
        # 1. Claim
        claimed_path = vault.claim_task(task_file)
        if not claimed_path:
            continue # Lost race

        logger.log_action("Claim", claimed_path, "SUCCESS")

        # 2. Process
        try:
            draft_reply(claimed_path)
            # 3. Move to Approval
            vault.move_to_approval(claimed_path, domain="email")
            logger.log_action("Draft", claimed_path, "SUCCESS", {"next": "Pending_Approval"})
            # 4. Notify Dashboard
            vault.write_update(f"Drafted reply for {task_file.name}")
        except Exception as e:
            logger.log_action("Process", claimed_path, "FAILED", {"error": str(e)})

def draft_reply(file_path):
    """Simulates drafting."""
    with open(file_path, "a", encoding="utf-8") as f:
        f.write("\n\n## AI Draft Reply\n")
        f.write("Hello,\n\nI have received your message. I am drafting this for executive review.\n\nBest,\nAI Employee")
    time.sleep(2)

if __name__ == "__main__":
    with open(str(ROOT / "cloud_agent_startup.log"), "w") as f:
        f.write(f"Starting at {time.ctime()}\n")
        f.write(f"Vault: {VAULT_PATH}\n")
        f.write(f"Agent: {AGENT_NAME}\n")
    
    print(f"Cloud Agent {AGENT_NAME} Online...")
    
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        process_needs_action()
        sys.exit(0)

    while True:
        try:
            process_needs_action()
        except Exception as e:
            with open(str(ROOT / "cloud_agent_loop_error.log"), "a") as f:
                f.write(f"Loop Error: {e}\n")
        time.sleep(5)
