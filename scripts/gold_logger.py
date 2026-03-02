#!/usr/bin/env python3
import os
import json
from datetime import datetime
from audit_logger import log_event

VAULT_LOGS = "AI_Employee_Vault/Logs"

def log_action(agent_tier, skill_name, action, status, details=None):
    """
    Legacy wrapper for log_action.
    Now redirects to audit_logger.log_event for unification.
    """
    # Use log_event for the new standardized audit trail
    log_event(
        source=f"{agent_tier}/{skill_name}",
        action=action,
        status=status,
        metadata=details
    )

if __name__ == "__main__":
    # Test log
    log_action("Gold", "SystemInit", "Logger Start", "SUCCESS", {"message": "Gold Tier Logging Online (Redirected to Audit)"})
    print("Log entry created via legacy wrapper.")
