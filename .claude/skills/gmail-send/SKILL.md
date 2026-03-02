# Skill: Gmail Send

## Overview
Automates sending emails via Gmail SMTP using SSL for secure communication. Designed for production workflows requiring notifications or reporting.

## Requirements
- `EMAIL_ADDRESS`: Gmail address for authentication.
- `EMAIL_PASSWORD`: Gmail App Password (NOT the primary password).

## Usage
Execute the script with recipient, subject, and body.

### Command
```bash
python scripts/send_email.py "recipient@example.com" "Project Update" "The task is complete."
```

## Inputs
1. `to`: Recipient email address.
2. `subject`: Email subject line.
3. `body`: Main email content.

## Outputs
- `Success: Email sent to [recipient]`
- `Error: [Detailed reason]`

## Implementation Details
- Uses `smtplib` with SSL (port 465).
- Supports plain text content.
- Graceful error handling for missing credentials and network issues.
