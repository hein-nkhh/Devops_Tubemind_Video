import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from .config import settings

def send_email(to_email: str, subject: str, body: str):
    msg = MIMEMultipart()
    msg['From'] = settings.EMAIL_FROM
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.sendmail(settings.EMAIL_FROM, to_email, msg.as_string())
            return True
    except Exception:
        return False