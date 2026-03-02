#!/usr/bin/env python3
import os
import time
import argparse
import uuid
import sys

VAULT_ROOT = "AI_Employee_Vault"
APPROVAL_DIR = os.path.join(VAULT_ROOT, "Needs_Approval")

def request_approval(action_description):
    # Ensure directory exists
    if not os.path.exists(APPROVAL_DIR):
        try:
            os.makedirs(APPROVAL_DIR, exist_ok=True)
        except Exception as e:
            print(f"Error: Failed to create approval directory. {str(e)}")
            sys.exit(1)

    # Generate a unique request file
    request_id = str(uuid.uuid4())[:8]
    filename = f"Approval_Request_{request_id}.md"
    filepath = os.path.join(APPROVAL_DIR, filename)

    # Request content template
    content = f"""# ⚠️ Approval Request - ID: {request_id}
    
## Proposed Action
{action_description}

## Instructions for Human
- To **APPROVE**: Add "APPROVED" anywhere in this file.
- To **REJECT**: Add "REJECTED" anywhere in this file.

---
Created: {time.strftime('%Y-%m-%d %H:%M:%S')}
"""
    try:
        with open(filepath, 'w') as f:
            f.write(content)
        
        print(f"Request created: {filename}")
        print("Waiting for human approval... (Edit the file to approve/reject)")

        # Blocking polling loop
        while True:
            time.sleep(2)  # 2-second interval to reduce CPU load
            
            if not os.path.exists(filepath):
                print("Error: Request file was deleted before a decision was recorded.")
                sys.exit(1)
            
            with open(filepath, 'r') as f:
                current_data = f.read().upper()
            
            if "APPROVED" in current_data:
                print("Status: APPROVED")
                os.remove(filepath)
                return True
            
            if "REJECTED" in current_data:
                print("Status: REJECTED")
                os.remove(filepath)
                return False

    except Exception as e:
        print(f"Error: Processing failed. {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Human-in-the-loop approval requester.")
    parser.add_argument("description", help="Description of the action for approval.")
    
    args = parser.parse_args()
    request_approval(args.description)
