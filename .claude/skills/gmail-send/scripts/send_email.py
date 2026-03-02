#!/usr/bin/env python3
import smtplib
import os
import argparse
import sys
from dotenv import load_dotenv

# Load environment variables from .env file (if present in project root)
load_dotenv()

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(to_email, subject, body):
    sender_email = os.environ.get('EMAIL_ADDRESS')
    sender_password = os.environ.get('EMAIL_PASSWORD')

    if not sender_email or not sender_password:
        print("Error: EMAIL_ADDRESS or EMAIL_PASSWORD environment variables not set.")
        sys.exit(1)

    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # Standard Gmail SMTP configuration
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
        
        print(f"Success: Email sent to {to_email}")

    except smtplib.SMTPAuthenticationError:
        print("Error: Authentication failed. Verify EMAIL_ADDRESS and EMAIL_PASSWORD (App Password).")
        sys.exit(1)
    except Exception as e:
        print(f"Error: Failed to send email. {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Production-ready Gmail sender.")
    parser.add_argument("to", help="Recipient email address")
    parser.add_argument("subject", help="Email subject")
    parser.add_argument("body", help="Email body content")
    
    args = parser.parse_args()
    send_email(args.to, args.subject, args.body)
