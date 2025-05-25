import requests
from loguru import logger
import os
import io
from dotenv import load_dotenv

load_dotenv() 

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# 自动分页，避免超出 Telegram 限制
def split_and_send(message: str, max_length: int = 4000):
    chunks = []
    lines = message.splitlines()
    current = ""
    for line in lines:
        if len(current) + len(line) + 1 > max_length:
            chunks.append(current)
            current = ""
        current += line + "\n"
    if current:
        chunks.append(current)

    for chunk in chunks:
        send(f"{chunk}")

def send_msg(str): 

    try:
        url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'

        payload = {
            'chat_id': CHAT_ID,
            'text': str
        }
        response = requests.post(url, data=payload)
        logger.info(response)
        
    except Exception as e:
        logger.error(f"send message err: {e}")
        
def send_file(text : str, title : str):
    
    try:
        file_like = io.StringIO(text)
        file_like.name = title

        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
        response = requests.post(
            url,
            data={"chat_id": CHAT_ID},
            files={"document": (file_like.name, file_like, "text/plain")}
        )

        if response.status_code == 200:
            logger.info(f"send file {title} ok")
        else:
            logger.error(f"send file {title} err")
            
    except Exception as e:
        logger.error(f"send file except: {e}")

def send_photo(buf :io.BytesIO, title): 
    
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"

        files = {'photo': (title, buf, 'image/png')}
        data = {'chat_id': CHAT_ID}

        response = requests.post(url, files=files, data=data)
            
        if response.status_code == 200:
            logger.info(f"send photo {title} ok")
        else:
            logger.error(f"send photo {title} err, {response.status_code}")
            
    except Exception as e:
        logger.error(f"send photo err: {e}")