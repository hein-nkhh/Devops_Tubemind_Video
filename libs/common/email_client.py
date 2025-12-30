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
    
    # SET CỨNG EMAIL_FROM TẠI ĐÂY
    fixed_email = "huyhoang.190904@gmail.com" 
    
    msg['From'] = fixed_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.ehlo() 
            
            # Sử dụng thông tin đăng nhập từ settings nhưng đăng nhập bằng đúng email đã set cứng
            if settings.SMTP_USER and settings.SMTP_PASSWORD:
                server.login(fixed_email, settings.SMTP_PASSWORD)
            
            server.send_message(msg)
            
        logger.info(f"Email sent successfully to {to_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return False