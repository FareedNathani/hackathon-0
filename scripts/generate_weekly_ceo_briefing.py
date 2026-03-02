#!/usr/bin/env python3
import os
import sys
import json
import glob
from datetime import datetime, timedelta

# Path configuration
AI_VAULT = "AI_Employee_Vault"
DONE_DIR = os.path.join(AI_VAULT, "Done")
ACCOUNTING_DIR = os.path.join(AI_VAULT, "Accounting")
SOCIAL_DIR = os.path.join(AI_VAULT, "Social")
LOGS_DIR = os.path.join(AI_VAULT, "Logs")
SCHEDULER_LOG = "scheduler.log"
OUTPUT_DIR = os.path.join("vault", "CEO", "Weekly_Briefings")

# Import audit_logger from same directory
sys.path.append(os.path.dirname(__file__))
from audit_logger import log_event, handle_failure

class WeeklyBriefingGenerator:
    def __init__(self):
        try:
            self.today = datetime.now()
            self.last_week = self.today - timedelta(days=7)
            os.makedirs(OUTPUT_DIR, exist_ok=True)
        except Exception as e:
            handle_failure("BriefingGeneratorInit", str(e))

    def is_recent(self, file_path):
        """Checks if a file was modified within the last 7 days."""
        try:
            mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
            return mtime > self.last_week
        except: return False

    def gather_completed_tasks(self):
        """Gathers task filenames completed in the last 7 days."""
        tasks = []
        try:
            for file in glob.glob(os.path.join(DONE_DIR, "*.md")):
                if self.is_recent(file):
                    tasks.append(os.path.basename(file))
        except Exception as e:
            log_event("BriefingGenerator", "Task Gathering Error", "ERROR", {"error": str(e)})
        return tasks

    def gather_accounting_data(self):
        """Reads sales data from Accounting folder (placeholder logic)."""
        sales_data = []
        try:
            for file in glob.glob(os.path.join(ACCOUNTING_DIR, "*")):
                if self.is_recent(file):
                    try:
                        with open(file, "r", encoding="utf-8") as f:
                            sales_data.append(f.read().strip())
                    except: pass
        except Exception as e:
            log_event("BriefingGenerator", "Accounting Gathering Error", "ERROR", {"error": str(e)})
        return sales_data

    def gather_social_metrics(self):
        """Reads social metrics from Social folder subdirs (placeholder logic)."""
        metrics = {"Facebook": [], "Instagram": [], "Twitter": []}
        try:
            for platform in metrics.keys():
                platform_dir = os.path.join(SOCIAL_DIR, platform)
                if os.path.exists(platform_dir):
                    for file in glob.glob(os.path.join(platform_dir, "*")):
                        if self.is_recent(file):
                            try:
                                with open(file, "r", encoding="utf-8") as f:
                                    metrics[platform].append(f.read().strip())
                            except: pass
        except Exception as e:
            log_event("BriefingGenerator", "Social Gathering Error", "ERROR", {"error": str(e)})
        return metrics

    def analyze_agent_performance(self):
        """Analyzes JSON logs for success/failure rates."""
        stats = {"total": 0, "success": 0, "failure": 0, "errors": []}
        try:
            for log_file in glob.glob(os.path.join(LOGS_DIR, "*.json")):
                if self.is_recent(log_file):
                    try:
                        with open(log_file, "r", encoding="utf-8") as f:
                            entries = json.load(f)
                            for entry in entries:
                                stats["total"] += 1
                                status = entry.get("status")
                                if status == "SUCCESS":
                                    stats["success"] += 1
                                elif status in ["ERROR", "FAILED", "CRITICAL"]:
                                    stats["failure"] += 1
                                    stats["errors"].append(f"{entry.get('source') or entry.get('skill')}: {entry.get('action')} - {status}")
                    except: pass
        except Exception as e:
            log_event("BriefingGenerator", "Performance Analysis Error", "ERROR", {"error": str(e)})
        return stats

    def gather_operational_issues(self):
        """Scans scheduler.log for recent errors."""
        recent_issues = []
        try:
            if os.path.exists(SCHEDULER_LOG):
                with open(SCHEDULER_LOG, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    for line in lines[-50:]:
                        if any(x in line.upper() for x in ["ERROR", "FAILED", "CRITICAL"]):
                            recent_issues.append(line.strip())
        except Exception as e:
            log_event("BriefingGenerator", "Operational Log Scan Error", "ERROR", {"error": str(e)})
        return recent_issues

    def generate(self):
        try:
            log_event("BriefingGenerator", "Weekly Generation", "PROCESSING")
            
            date_str = self.today.strftime("%Y-%m-%d")
            filename = f"CEO_Weekly_Briefing_{date_str}.md"
            filepath = os.path.join(OUTPUT_DIR, filename)

            tasks = self.gather_completed_tasks()
            sales = self.gather_accounting_data()
            social = self.gather_social_metrics()
            perf = self.analyze_agent_performance()
            issues = self.gather_operational_issues()

            efficiency = (perf["success"] / perf["total"] * 100) if perf["total"] > 0 else 0

            content = f"# \U0001F454 Weekly CEO Executive Briefing\n"
            content += f"**Date:** {date_str}\n"
            content += f"**Reporting Period:** {self.last_week.strftime('%Y-%m-%d')} to {date_str}\n\n"

            content += "## \U0001F4D3 Executive Summary\n"
            content += f"The AI Employee Factory has completed {len(tasks)} tasks this week. System efficiency is currently at {efficiency:.1f}%. Key focuses were task automation and social media readiness.\n\n"

            content += "## \U0001F4B0 Financial Overview\n"
            if sales:
                content += "\n".join([f"- {s}" for s in sales]) + "\n\n"
            else:
                content += "No new sales data recorded in AI_Employee_Vault/Accounting this week.\n\n"

            content += "## \U0001F4C8 Marketing Performance\n"
            has_social = False
            for platform, data in social.items():
                if data:
                    has_social = True
                    content += f"### {platform}\n" + "\n".join([f"- {d}" for d in data]) + "\n\n"
            if not has_social:
                content += "No marketing metrics recorded this week in AI_Employee_Vault/Social.\n\n"

            content += "## \u26A0\uFE0F Operational Issues\n"
            if issues:
                content += "\n".join([f"- {i}" for i in issues[:5]]) + "\n\n"
            else:
                content += "No critical operational issues detected in system logs.\n\n"

            content += "## \U0001F916 AI Agent Efficiency\n"
            content += f"- **Total Actions:** {perf['total']}\n"
            content += f"- **Successful Cycles:** {perf['success']}\n"
            content += f"- **Failure Count:** {perf['failure']}\n"
            content += f"- **Overall Efficiency:** {efficiency:.1f}%\n\n"

            content += "### Agent Error Details:\n"
            if perf["errors"]:
                content += "\n".join([f"- {e}" for e in set(perf["errors"][:10])]) + "\n\n"
            else:
                content += "No agent-level errors recorded this week.\n\n"

            content += "## \U0001F4A1 Recommendations\n"
            content += "1. **Accounting Integration:** Automate data export from Odoo to the Accounting folder to enable financial reporting.\n"
            content += "2. **Social Content:** Increase the frequency of automated posts to gather more engagement metrics.\n"
            content += "3. **Error Mitigation:** Investigate repeated errors in skill execution to improve efficiency toward 100%.\n"

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)

            log_event("BriefingGenerator", "Weekly Generation", "SUCCESS", {"file": filepath})
            return filepath
        except Exception as e:
            handle_failure("BriefingGenerator", str(e))
            return None

if __name__ == "__main__":
    try:
        generator = WeeklyBriefingGenerator()
        report = generator.generate()
        if report:
            print(f"Weekly Briefing Generated Successfully: {report}")
    except Exception as e:
        handle_failure("BriefingGeneratorMain", str(e))
        sys.exit(0) # Never crash with exit 1 if possible
