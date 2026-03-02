# Skill: Human Approval

## Overview
Enables a high-security "human-in-the-loop" workflow for sensitive actions. Pauses agent activity by creating an approval request file and monitoring for user confirmation.

## Requirements
- `AI_Employee_Vault/Needs_Approval/` directory for tracking requests.

## Usage
Execute the script with a description of the proposed action.

### Command
```bash
python scripts/request_approval.py "Proceed with database migration?"
```

## Inputs
1. `description`: Detailed explanation of the action requiring human review.

## Outputs
- `Status: APPROVED` (if file contains "APPROVED")
- `Status: REJECTED` (if file contains "REJECTED")
- `Error: [Reason]`

## Implementation Details
- Generates unique `.md` files in `AI_Employee_Vault/Needs_Approval/`.
- Uses polling (2s interval) to detect state changes within the markdown file.
- Automatically cleans up request files after a decision is recorded.
- Blocks execution until a resolution is reached or an error occurs.
