# 👔 AI Employee Factory: Gold Tier Setup Guide

## 🚀 Overview
The Gold Tier AI Employee Factory is a fully autonomous, reliable, and secure agentic system. It features dual background loops, unified audit logging, and executive-level reporting.

## 🛠️ Installation & Setup
1. **Configure Secrets**: Update the `.env` file in the root directory with your actual API keys:
   - `ODOO_URL`, `ODOO_DB`, `ODOO_USER`, `ODOO_PASSWORD`
   - `FB_ACCESS_TOKEN`, `FB_PAGE_ID`
   - `INSTA_ACCESS_TOKEN`, `INSTA_ID`
   - `X_CONSUMER_KEY`, `X_CONSUMER_SECRET`, etc.

2. **Start the System**: Run the main batch file:
   ```bash
   ./run_platinum_factory.bat
   ```
   This will open two windows:
   - **Task Loop**: Processes Inbox, creates plans, and executes skills.
   - **Autonomous Loop**: Scans for system inefficiencies every 30 minutes.

3. **Monitor Activity**:
   - Check `AI_Employee_Vault/Logs/` for real-time JSON audit trails.
   - Use the Obsidian vault to view `vault/CEO/Weekly_Briefings/` (Sundays) and `vault/Ralph/` (Efficiency reports).

## 🛡️ Reliability & Recovery
- **Failure Recovery**: Any task that causes a script error is automatically logged and moved to `AI_Employee_Vault/Needs_Action/` with a `FAILED_` prefix.
- **Never-Crash Architecture**: All background loops are protected by top-level exception handlers and will heartbeat indefinitely.
- **Health Check**: Run `python scripts/gold_health_check.py` at any time to verify system integrity.

## 📊 Reporting
- **Weekly CEO Briefing**: Automatically triggers every Sunday at midnight (server time).
- **Audit Logs**: Standardized format including `timestamp`, `source`, `action`, `status`, and `metadata`.

---
**Status:** Gold Tier Operational
**Lead Agent:** Ralph Wiggum
