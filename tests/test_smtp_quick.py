#!/usr/bin/env python3
"""Quick email test without Django - just test SMTP connectivity"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_test_email():
    """Send a simple test email to smtp4dev"""
    smtp_host = "localhost"
    smtp_port = 2525
    from_email = "test@idrissimart.local"
    to_email = "test@example.com"

    try:
        # Create message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Test Email - Signal Integration"
        msg["From"] = from_email
        msg["To"] = to_email

        html = """
        <html>
        <body style="font-family: Arial; padding: 20px;">
            <h2 style="color: #4b315e;">Email Integration Test</h2>
            <p>This is a test email to verify smtp4dev connectivity.</p>
            <p><strong>Status:</strong> ✓ Connection successful</p>
        </body>
        </html>
        """

        html_part = MIMEText(html, "html", "utf-8")
        msg.attach(html_part)

        # Send email
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.send_message(msg)

        print("✓ Email sent successfully!")
        print(f"📧 Check your email at: http://localhost:3100")
        return True

    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False


if __name__ == "__main__":
    send_test_email()
