#!/usr/bin/env python3
import os
import shutil
import argparse
import sys

# Define target vault structure relative to the project root
VAULT_ROOT = "AI_Employee_Vault"
VALID_FOLDERS = ["Inbox", "Needs_Action", "Done", "Needs_Approval"]

def move_task(source_path, target_folder):
    # Ensure source exists (checking both relative and full paths)
    if not os.path.exists(source_path):
        print(f"Error: File '{source_path}' does not exist.")
        sys.exit(1)
    
    # Ensure destination folder is one of the valid workflow stages
    if target_folder not in VALID_FOLDERS:
        print(f"Error: Invalid destination '{target_folder}'. Must be one of: {', '.join(VALID_FOLDERS)}.")
        sys.exit(1)
    
    # Build absolute-like destination path
    # Assume script is run from project root or relative to it
    filename = os.path.basename(source_path)
    dest_dir = os.path.join(VAULT_ROOT, target_folder)
    
    # Ensure destination directory actually exists
    if not os.path.isdir(dest_dir):
        try:
            os.makedirs(dest_dir, exist_ok=True)
        except Exception as e:
            print(f"Error: Failed to create destination directory. {str(e)}")
            sys.exit(1)
            
    dest_path = os.path.join(dest_dir, filename)
    
    try:
        # Avoid overwriting existing files without a plan (optional behavior)
        if os.path.exists(dest_path):
            # Append a timestamp or version if necessary, but here we just notify
            print(f"Warning: Overwriting existing file at '{dest_path}'.")
            
        shutil.move(source_path, dest_path)
        print(f"Success: Moved '{filename}' to '{target_folder}'.")

    except Exception as e:
        print(f"Error: Failed to move file. {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Workflow task manager.")
    parser.add_argument("source", help="Path to the file to move.")
    parser.add_argument("target", help="Target workflow stage (e.g., Needs_Action).")
    
    args = parser.parse_args()
    move_task(args.source, args.target)
