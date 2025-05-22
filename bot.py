from telegram import Bot
from telegram.constants import ParseMode
import asyncio
from telegram.error import TelegramError
from loguru import logger
import os
 
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

bot = Bot(token=BOT_TOKEN)

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
        asyncio.run(send(f"```{chunk}```"))

async def send(str): 
    
    try:
        await bot.send_message(
            chat_id=CHAT_ID,
            text=str,
            parse_mode=ParseMode.MARKDOWN
        )
    except TelegramError as e:
        logger.error(f"Telegram API 错误: {e}")
    except Exception as e:
        logger.error(f"发生其他错误: {e}")