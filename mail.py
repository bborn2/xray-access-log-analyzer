import smtplib
from email.message import EmailMessage
import os
from loguru import logger
from email.utils import make_msgid
from io import BytesIO
from PIL import Image

MAIL_LOGIN_USER = os.getenv("MAIL_LOGIN_USER")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
MAIL_SERVER = os.getenv("MAIL_SERVER")

def send_email(fr, to, subject, content, image_buffer):

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = fr
    msg['To'] = to
    
    image_cid = make_msgid(domain='xyz.com')  # domain 可任意填
    image_cid_stripped = image_cid[1:-1]  # 去掉尖括号 <>

    # HTML 内容引用图片
    html_content = f"""
    <html>
    <body>
    <pre style="font-family: monospace; font-size: 14px;">
        {content}
        </pre>
        <p>chart:</p>
        <img src="cid:{image_cid_stripped}">
    </body>
    </html>
    """

    msg.set_content(content)
    
    image_bytes = image_buffer.getvalue()
    msg.add_alternative(html_content, subtype='html')
    msg.get_payload()[1].add_related(image_bytes, maintype='image', subtype='png', cid=f"<{image_cid}>")

    smtp_server = MAIL_SERVER
    smtp_port = 587

    your_email = MAIL_LOGIN_USER
    your_app_password = MAIL_PASSWORD
    
    logger.info(msg)

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(your_email, your_app_password)
            server.send_message(msg)
            logger.info("mail send ok")
    except Exception as e:
        logger.error(f"mail send fail: {e}")
