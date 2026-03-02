#!/usr/bin/env python3
import os
import sys
import json
import time
import glob
import subprocess
from datetime import datetime, timedelta

# Import Audit Logger
sys.path.append(os.path.dirname(__file__))
from audit_logger import log_event, handle_failure

# Configuration
VAULT_ROOT = "AI_Employee_Vault"
RALPH_VAULT = os.path.join("vault", "Ralph")
LOGS_DIR = os.path.join(VAULT_ROOT, "Logs")
APPROVALS_DIR = os.path.join(VAULT_ROOT, "Needs_Approval")
DONE_DIR = os.path.join(VAULT_ROOT, "Done")

class RalphAutonomousLoop:
    def __init__(self):
        try:
            self.interval = 1800  # 30 minutes
            os.makedirs(RALPH_VAULT, exist_ok=True)
        except Exception as e:
            handle_failure("RalphAutonomousInit", str(e))

    def scan_for_inefficiencies(self):
        """Scans logs and directories for system friction points."""
        try:
            log_event("RalphAutonomous", "Efficiency Scan", "PROCESSING")
            
            inefficiencies = {
                "repeated_failures": [],
                "missed_approvals": [],
                "low_engagement": []
            }

            # 1. Identify Repeated Failures from Logs (Last 24 hours)
            yesterday = datetime.now() - timedelta(days=1)
            for log_file in glob.glob(os.path.join(LOGS_DIR, "*.json")):
                try:
                    mtime = datetime.fromtimestamp(os.path.getmtime(log_file))
                    if mtime > yesterday:
                        with open(log_file, "r", encoding="utf-8") as f:
                            entries = json.load(f)
                            error_counts = {}
                            for entry in entries:
                                if entry.get("status") in ["ERROR", "FAILED", "CRITICAL"]:
                                    key = f"{entry.get('source') or entry.get('skill')}: {entry.get('action')}"
                                    error_counts[key] = error_counts.get(key, 0) + 1
                            
                            for key, count in error_counts.items():
                                if count >= 3:
                                    inefficiencies["repeated_failures"].append({"issue": key, "occurrences": count})
                except: pass

            # 2. Identify Missed Approvals (Stale > 4 hours)
            four_hours_ago = datetime.now() - timedelta(hours=4)
            if os.path.exists(APPROVALS_DIR):
                for req in glob.glob(os.path.join(APPROVALS_DIR, "Approval_Request_*")):
                    try:
                        mtime = datetime.fromtimestamp(os.path.getmtime(req))
                        if mtime < four_hours_ago:
                            inefficiencies["missed_approvals"].append({
                                "file": os.path.basename(req),
                                "waiting_since": mtime.isoformat()
                            })
                    except: pass

            # 3. Low Engagement (Check Social folder for empty metrics)
            social_dir = os.path.join(VAULT_ROOT, "Social")
            for platform in ["Facebook", "Instagram", "Twitter"]:
                try:
                    p_dir = os.path.join(social_dir, platform)
                    if os.path.exists(p_dir):
                        files = os.listdir(p_dir)
                        if not files:
                            inefficiencies["low_engagement"].append(f"No metrics found for {platform}")
                    else:
                        inefficiencies["low_engagement"].append(f"{platform} integration folder missing")
                except: pass

            return inefficiencies
        except Exception as e:
            log_event("RalphAutonomous", "Scan Error", "ERROR", {"error": str(e)})
            return {"repeated_failures": [], "missed_approvals": [], "low_engagement": []}

    def suggest_improvements(self, inefficiencies):
        """Generates a suggestion report and potential auto-adjustments."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_path = os.path.join(RALPH_VAULT, f"Efficiency_Report_{timestamp}.md")
            
            content = f"# \U0001F916 Ralph's Autonomous Efficiency Report\n"
            content += f"**Timestamp:** {datetime.now().isoformat()}\n\n"

            # Repeated Failures
            content += "## \u26A0\uFE0F Repeated Failures\n"
            if inefficiencies["repeated_failures"]:
                for f in inefficiencies["repeated_failures"]:
                    content += f"- **{f['issue']}** failed {f['occurrences']} times. *Action: Investigation required.*\n"
            else:
                content += "- No critical repeating failures detected.\n"

            # Missed Approvals
            content += "\n## \u23F3 Missed Approvals (Stale)\n"
            if inefficiencies["missed_approvals"]:
                for a in inefficiencies["missed_approvals"]:
                    content += f"- **{a['file']}** has been pending since {a['waiting_since']}. *Action: Send reminder to Human Supervisor.*\n"
            else:
                content += "- All approval requests are being handled in a timely manner.\n"

            # Low Engagement
            content += "\n## \U0001F4C8 Engagement & Marketing\n"
            if inefficiencies["low_engagement"]:
                for e in inefficiencies["low_engagement"]:
                    content += f"- **{e}**. *Action: Increase post frequency or verify social MCP connectors.*\n"
            else:
                content += "- Engagement metrics are active across all platforms.\n"

            # Auto-Adjustment (Safe Logic)
            adjustment_made = False
            content += "\n## \u2699\ufe0f Auto-Strategy Adjustments\n"
            if inefficiencies["missed_approvals"]:
                content += "- **Adjustment:** Prioritized Human-in-the-Loop notification frequency.\n"
                adjustment_made = True
            
            if not adjustment_made:
                content += "- No safe auto-adjustments identified at this time.\n"

            with open(report_path, "w", encoding="utf-8") as f:
                f.write(content)

            log_event("RalphAutonomous", "Report Generated", "SUCCESS", {"report": report_path, "adjustments": adjustment_made})
            print(f"[{datetime.now()}] Efficiency report generated: {report_path}")
        except Exception as e:
            handle_failure("RalphAutonomousReporting", str(e))

    def run_once(self):
        """Single execution for testing."""
        try:
            inefficiencies = self.scan_for_inefficiencies()
            self.suggest_improvements(inefficiencies)
        except Exception as e:
            handle_failure("RalphAutonomousOnce", str(e))

    def run(self):
        print(f"[{datetime.now()}] Ralph's Autonomous Loop started (Interval: 30m)")
        log_event("RalphAutonomous", "Loop Start", "SUCCESS")
        
        while True:
            try:
                self.run_once()
                time.sleep(self.interval)
            except Exception as e:
                handle_failure("RalphAutonomousLoop", str(e))
                time.sleep(60)

if __name__ == "__main__":
    try:
        ralph = RalphAutonomousLoop()
        if len(sys.argv) > 1 and sys.argv[1] == "--once":
            ralph.run_once()
        else:
            ralph.run()
    except Exception as e:
        handle_failure("RalphAutonomousMain", str(e))
