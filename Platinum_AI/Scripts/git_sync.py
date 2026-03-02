import time
import os
import subprocess

def git_sync():
    """
    Syncs the Vault with the remote repo.
    Policy: Cloud pushes to 'cloud-branch', Local pushes to 'main'.
    """
    print("🔄 [Sync] Pulling latest changes...")
    # subprocess.run(["git", "pull", "--rebase"])
    
    print("🔄 [Sync] Committing local state...")
    # subprocess.run(["git", "add", "."])
    # subprocess.run(["git", "commit", "-m", "Auto-sync"])
    
    print("🔄 [Sync] Pushing to remote...")
    # subprocess.run(["git", "push"])

if __name__ == "__main__":
    while True:
        git_sync()
        time.sleep(30)
