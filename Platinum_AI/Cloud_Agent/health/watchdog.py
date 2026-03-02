import time
import psutil
import smtplib
from email.mime.text import MIMEText

class HealthMonitor:
    def __init__(self, alert_email):
        self.alert_email = alert_email

    def check_disk(self):
        du = psutil.disk_usage('/')
        if du.percent > 90:
            self.alert(f"Disk Space Critical: {du.percent}% used")

    def check_process(self, name):
        found = False
        for proc in psutil.process_iter(['name', 'cmdline']):
            if name in proc.info['name'] or (proc.info['cmdline'] and name in proc.info['cmdline'][0]):
                found = True
                break
        if not found:
            self.alert(f"Process {name} is DOWN!")

    def alert(self, message):
        print(f"🚨 ALERT: {message}")
        # In prod: send actual email via local SMTP or MCP
        
    def heartbeat(self):
        with open("Status.md", "w") as f:
            f.write(f"**System Status:** ONLINE
**Time:** {time.ctime()}
")

if __name__ == "__main__":
    monitor = HealthMonitor("admin@example.com")
    while True:
        monitor.check_disk()
        monitor.check_process("cloud_orchestrator")
        monitor.heartbeat()
        time.sleep(60)
