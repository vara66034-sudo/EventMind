import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

# Настройки SMTP
SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.mail.ru")
SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")

def send_email(to_email: str, subject: str, html_content: str):
    print(f"\n[EMAIL SIMULATION] To: {to_email} | Subject: {subject}")
    print(f"[EMAIL CONTENT] {html_content}\n")
    
    if not SMTP_USER or not SMTP_PASSWORD:
        print("[!] SMTP credentials missing in .env. Email was only simulated in console.")
        return

    try:
        msg = MIMEMultipart()
        msg['From'] = f"EventMind <{SMTP_USER}>"
        msg['To'] = to_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(html_content, 'html'))
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"Email successfully sent to {to_email}")
    except Exception as e:
        print(f"Failed to send email via SMTP: {e}")
