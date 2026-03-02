import json
import time
import os
from pathlib import Path

class AuditLogger:
    def __init__(self, log_dir, agent_name):
        self.log_dir = Path(log_dir)
        self.agent_name = agent_name
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def log_action(self, action_type, target, status, details=None):
        """
        Logs an action to a daily JSON file.
        schema: {timestamp, agent, action, target, status, details}
        """
        entry = {
            "timestamp": time.time(),
            "iso_time": time.ctime(),
            "agent": self.agent_name,
            "action": action_type,
            "target": str(target),
            "status": status,
            "details": details or {}
        }

        date_str = time.strftime("%Y-%m-%d")
        log_file = self.log_dir / f"audit_{date_str}.json"

        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception as e:
            print(f"CRITICAL: Failed to write audit log! {e}")
