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
    sender = settings.EMAIL_FROM or settings.SMTP_USER
    msg['From'] = settings.EMAIL_FROM
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Sử dụng 'with' để tự động đóng kết nối
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.ehlo() # Định danh với server
            server.starttls() # Bảo mật kết nối
            server.ehlo() 
            
            if settings.SMTP_USER and settings.SMTP_PASSWORD:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            
            server.send_message(msg) # Dùng send_message thay vì sendmail sẽ chuẩn hơn với MIMEMultipart
            
        logger.info(f"Email sent successfully to {to_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return False