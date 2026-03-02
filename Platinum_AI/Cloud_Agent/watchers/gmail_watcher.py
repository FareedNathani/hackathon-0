import time
import os
from pathlib import Path

class GmailWatcher:
    def __init__(self, output_dir):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def check_mail(self):
        """
        Mock Gmail Watcher.
        In prod, use Gmail API via MCP.
        Here we simulate arrival for the demo.
        """
        # Logic to check API would go here
        pass

    def inject_mock_email(self, subject, sender):
        """Helper for the demo scenario."""
        filename = f"email_{int(time.time())}.md"
        path = self.output_dir / filename
        
        content = f"""# Email Task
**From:** {sender}
**Subject:** {subject}
**Status:** Unread

Please draft a reply to this inquiry.
"""
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        
        print(f"📧 [Gmail Watcher] New email injected: {filename}")
        return path

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent.parent.parent / ".env.cloud")
    vault_root = os.getenv("VAULT_PATH", "./Vault")
    
    # Test run
    w = GmailWatcher(Path(vault_root) / "Needs_Action" / "email")
    w.inject_mock_email("Urgent: Project Update", "vip@client.com")
