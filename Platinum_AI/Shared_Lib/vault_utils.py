import os
import shutil
import time
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class VaultManager:
    def __init__(self, vault_root, agent_id):
        self.root = Path(vault_root)
        self.agent_id = agent_id
        self.in_progress_dir = self.root / "In_Progress" / self.agent_id
        self.in_progress_dir.mkdir(parents=True, exist_ok=True)

    def claim_task(self, file_path):
        """
        Implements Claim-by-Move concurrency.
        Attempts to atomically move a file from Needs_Action to In_Progress.
        Returns new path if successful, None if failed (race condition).
        """
        source = Path(file_path)
        if not source.exists():
            logging.warning(f"Failed to claim {source}: File gone (race condition?)")
            return None

        dest = self.in_progress_dir / source.name
        
        try:
            shutil.move(str(source), str(dest))
            logging.info(f"Claimed task: {source.name} -> {dest}")
            return dest
        except Exception as e:
            logging.error(f"Claim failed for {source.name}: {e}")
            return None

    def move_to_approval(self, file_path, domain="general"):
        """Moves task to Pending_Approval after drafting."""
        dest_dir = self.root / "Pending_Approval" / domain
        dest_dir.mkdir(parents=True, exist_ok=True)
        return self._safe_move(file_path, dest_dir)

    def move_to_done(self, file_path):
        """Moves task to Done."""
        dest_dir = self.root / "Done"
        dest_dir.mkdir(parents=True, exist_ok=True)
        return self._safe_move(file_path, dest_dir)

    def _safe_move(self, src, dest_dir):
        src = Path(src)
        dest = dest_dir / src.name
        try:
            shutil.move(str(src), str(dest))
            logging.info(f"Moved {src.name} to {dest_dir}")
            return dest
        except Exception as e:
            logging.error(f"Move failed: {e}")
            return None

    def write_update(self, message):
        """Writes an update signal for the Dashboard."""
        timestamp = int(time.time())
        filename = f"Update_{self.agent_id}_{timestamp}.md"
        path = self.root / "Updates" / filename
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"**Agent:** {self.agent_id}\n")
            f.write(f"**Time:** {time.ctime()}\n")
            f.write(f"**Update:** {message}\n")
        return path
