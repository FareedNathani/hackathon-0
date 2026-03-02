import os
import time
import sys
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Import audit logger
sys.path.append(os.path.abspath('scripts'))
from audit_logger import log_event, handle_failure

class InboxHandler(FileSystemEventHandler):
    """Handles file system events in the vault/Inbox folder."""

    def on_created(self, event):
        """Called when a new file or folder is created."""
        try:
            if not event.is_directory and event.src_path.endswith('.md'):
                src_path = event.src_path
                filename = os.path.basename(src_path)
                
                log_event("Watcher", "File Detected", "SUCCESS", {"file": filename})
                
                # Generate timestamp for the plan filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                dest_filename = f"Plan_{timestamp}.md"
                dest_path = os.path.join('vault', 'Needs_Action', dest_filename)
                
                # Briefly wait to ensure the file is fully written
                time.sleep(0.5) # Increased for stability
                
                try:
                    with open(src_path, 'r', encoding='utf-8') as f:
                        original_task = f.read()
                    
                    # Logic to determine priority and human approval (simulated)
                    priority = "Medium"
                    requires_approval = "Yes"
                    if "urgent" in original_task.lower():
                        priority = "High"
                    
                    # Create the detailed plan content
                    plan_content = f"""# Task Plan

## Original Task
{original_task}

## Objective
To successfully address and complete the request defined in '{filename}'.

## Step-by-Step Plan
1. Review the original task requirements.
2. Gather necessary resources and data.
3. Execute the sub-tasks in sequence.
4. Verify the output against the objective.
5. Finalize and move to 'Done'.

## Priority
{priority}

## Requires Human Approval?
{requires_approval}

## Suggested Output
A completed response or set of files as requested in the original task.
"""
                    
                    # Write the plan file
                    with open(dest_path, 'w', encoding='utf-8') as f:
                        f.write(plan_content)
                    
                    print(f"Reasoning complete. Created Plan: '{dest_filename}' in 'vault/Needs_Action/'.")
                    log_event("Watcher", "Plan Generated", "SUCCESS", {"plan": dest_filename, "source": filename})
                except Exception as e:
                    # Move source file to Needs_Action on failure
                    print(f"Error creating plan for {filename}: {e}")
                    handle_failure("Watcher", str(e), src_path)
        except Exception as e:
            # Global catch to prevent thread crash
            log_event("WatcherThread", "Unhandled Exception", "CRITICAL", {"error": str(e)})

if __name__ == "__main__":
    try:
        # Ensure the required directories exist
        os.makedirs(os.path.join('vault', 'Inbox'), exist_ok=True)
        os.makedirs(os.path.join('vault', 'Needs_Action'), exist_ok=True)
        
        # Path to watch
        path_to_watch = os.path.join('vault', 'Inbox')
        
        # Initialize the event handler and the observer
        event_handler = InboxHandler()
        observer = Observer()
        observer.schedule(event_handler, path_to_watch, recursive=False)
        
        # Start the observer
        print(f"Monitoring '{path_to_watch}' for new .md files...")
        observer.start()
        
        while True:
            # Keep the script running
            time.sleep(1)
    except KeyboardInterrupt:
        # Stop the observer on manual exit
        observer.stop()
        print("\nStopping watcher...")
    except Exception as e:
        log_event("Watcher", "Global Crash Prevention", "CRITICAL", {"error": str(e)})
        # Infinite restart or wait could be here, but sleep to keep loop alive
        time.sleep(60)
    
    observer.join()
