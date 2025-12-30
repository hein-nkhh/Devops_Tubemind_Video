# import smtplib
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# from .config import settings

# def send_email(to_email: str, subject: str, body: str):
#     msg = MIMEMultipart()
#     msg['From'] = settings.EMAIL_FROM
#     msg['To'] = to_email
#     msg['Subject'] = subject
#     msg.attach(MIMEText(body, 'plain'))

#     try:
#         with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
#             server.sendmail(settings.EMAIL_FROM, to_email, msg.as_string())
#             return True
#     except Exception:
#         return False

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from .config import settings
from .logger import get_logger # Import logger để debug

logger = get_logger("email-client")

def send_email(to_email: str, subject: str, body: str):
    msg = MIMEMultipart()
    msg['From'] = settings.EMAIL_FROM
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        # MailHog dùng port 1025, AWS SES dùng port 587
        server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
        
        # [QUAN TRỌNG] Bật chế độ mã hoá TLS nếu không phải localhost
        if settings.SMTP_USER and settings.SMTP_PASSWORD:
            server.starttls() 
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        
        server.sendmail(settings.EMAIL_FROM, to_email, msg.as_string())
        server.quit()
        
        logger.info(f"Email sent successfully to {to_email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return False