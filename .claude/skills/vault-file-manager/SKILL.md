# Skill: Vault File Manager

## Overview
Automates file movement within the `AI_Employee_Vault` directory structure. Enforces organized task transitions and ensures operational data is in the correct lifecycle stage.

## Requirements
- `AI_Employee_Vault/` base directory with subfolders: `Inbox`, `Needs_Action`, `Done`, `Needs_Approval`.

## Usage
Execute the script with the source file path and the target folder.

### Command
```bash
python scripts/move_task.py "AI_Employee_Vault/Inbox/task_01.md" "Needs_Action"
```

## Inputs
1. `file_path`: Path to the file needing relocation.
2. `destination`: Target folder name (e.g., `Done`).

## Outputs
- `Success: Moved [filename] to [destination].`
- `Error: [Detailed failure reason]`

## Implementation Details
- Relocates files using `shutil.move` for atomic operations.
- Validates the existence of the source file and the destination folder.
- Normalizes paths to support relative and absolute addressing within the vault.
