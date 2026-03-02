# 🏆 Platinum Tier AI Employee (Digital FTE)

## 🚀 Overview
This is a production-ready, always-on AI Employee system designed for the 2026 Hackathon. It features a hybrid **Cloud + Local** architecture, ensuring 24/7 availability for low-risk tasks while keeping high-risk executive actions securely on local hardware.

## 🏗️ Architecture

### 1. Cloud Agent (Always-On VM)
- **Role**: Triage, Drafting, Monitoring.
- **Security**: Draft-only permissions. Cannot send money or final emails.
- **Tech**: Python Orchestrator, Odoo Draft MCP, Nginx Reverse Proxy.

### 2. Local Executive (Your Laptop)
- **Role**: Approval, Final Execution, Banking.
- **Security**: Full permissions. Only runs when you are online.
- **Tech**: Local Python Executor, WhatsApp Session, Hardware Keys.

### 3. The Vault (Shared Brain)
- **Sync**: Git-based sync (Cloud pushes to `cloud-branch`, Local merges).
- **Concurrency**: "Claim-by-Move" protocol.
    - Files in `/Needs_Action` are free game.
    - Moving file to `/In_Progress/<agent_id>/` claims it.

## 🛠️ Deployment Guide

### Step 1: Cloud Setup (Oracle/AWS)
1. Provision VM (Ubuntu 22.04).
2. Clone repo to `~/Platinum_AI`.
3. Copy `.env.cloud.example` to `.env`.
4. Start Odoo:
   ```bash
   cd Platinum_AI/Deployment
   docker-compose -f docker-compose.odoo.yml up -d
   ```
5. Start Cloud Agent:
   ```bash
   pm2 start Platinum_AI/Cloud_Agent/cloud_orchestrator.py --interpreter python3
   ```

### Step 2: Local Setup
1. Clone repo to `D:/Platinum_AI`.
2. Copy `.env.local.example` to `.env`.
3. Start Local Executive:
   ```bash
   python Platinum_AI/Local_Agent/local_orchestrator.py
   ```

### Step 3: The Demo Scenario
1. **Trigger**: Inject mock email into Cloud Watcher.
   ```bash
   python Platinum_AI/Cloud_Agent/watchers/gmail_watcher.py
   ```
2. **Observe**: Cloud Agent claims it, drafts reply, moves to `/Pending_Approval`.
3. **Approve**: Manually move file from `/Pending_Approval` to `/Approved`.
4. **Execute**: Local Agent detects approval, sends email, updates Dashboard.

## 🛡️ Security Model
- **Secrets**: Never synced via Git. separate `.env` files.
- **Isolation**: Cloud Odoo user has "Draft Only" ACLs.
- **Audit**: All actions logged to `Vault/Logs/audit_YYYY-MM-DD.json`.

## 📊 Monitoring
- **Health**: `Status.md` updated every 60s.
- **Watchdog**: Alerts admin if `cloud_orchestrator` process dies.

---
**Status**: PLATINUM TIER READY
**Version**: 2026.1.0
