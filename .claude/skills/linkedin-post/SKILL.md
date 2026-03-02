# Skill: LinkedIn Post

## Overview
Automates the creation of LinkedIn text posts using browser automation (Playwright). Designed for social media management and professional presence.

## Requirements
- `LINKEDIN_EMAIL`: LinkedIn account email.
- `LINKEDIN_PASSWORD`: LinkedIn account password.
- Playwright must be installed and initialized.

## Usage
Execute the script with post content.

### Command
```bash
python scripts/post_linkedin.py "Automating LinkedIn with Python and Playwright!"
```

## Inputs
1. `content`: Text to be posted.

## Outputs
- `Success: LinkedIn post created.`
- `Error: [Detailed failure reason]`

## Implementation Details
- Uses `Playwright` for headless browser interaction.
- Automates login and post creation workflows.
- Handles common navigation errors and timeouts.
- Note: May be affected by LinkedIn's anti-automation or 2FA policies.
