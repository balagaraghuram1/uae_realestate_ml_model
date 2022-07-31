"""Email notification service for alerts and reports."""
import os, logging, smtplib
from typing import List, Dict
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)

class EmailService:
    """Send email notifications for platform alerts."""

    def __init__(self, smtp_host: str = None, smtp_port: int = 587):
        self.smtp_host = smtp_host or os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = smtp_port
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_pass = os.getenv("SMTP_PASS", "")
        self.from_email = os.getenv("FROM_EMAIL", "noreply@uae-realestate-ml.com")

    def send_alert(self, subject: str, body: str, recipients: List[str]) -> bool:
        """Send an alert email."""
        msg = MIMEMultipart()
        msg["From"] = self.from_email
        msg["To"] = ", ".join(recipients)
        msg["Subject"] = f"[UAE RE ML] {subject}"
        msg.attach(MIMEText(body, "html"))
        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                if self.smtp_user and self.smtp_pass:
                    server.login(self.smtp_user, self.smtp_pass)
                server.send_message(msg)
            logger.info("Alert sent: %s to %d recipients", subject, len(recipients))
            return True
        except Exception as e:
            logger.error("Failed to send alert: %s", e)
            return False

    def send_report(self, report_data: Dict, recipients: List[str]) -> bool:
        """Send a formatted report email."""
        html = f"<h2>UAE Real Estate Market Report</h2>"
        for section, data in report_data.items():
            html += f"<h3>{section}</h3><pre>{data}</pre>"
        return self.send_alert("Market Report", html, recipients)
