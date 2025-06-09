# logger.py
import logging
import sys
from config import LOG_FILE
import os

os.makedirs('logs', exist_ok=True)

LOG_FILE = LOG_FILE

LOG_FORMAT = '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s'

# Основна конфігурація логів
logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Головний логер
logger = logging.getLogger("bot")

# Окремі логери
gpt_logger = logging.getLogger("services")
quiz_logger = logging.getLogger("quiz")
dialog_logger = logging.getLogger("dialog")
util_logger = logging.getLogger("util")

# Вимкнення зайвого шуму
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("telegram.ext._application").setLevel(logging.WARNING)
logging.getLogger("telegram.bot").setLevel(logging.WARNING)
logging.getLogger("apscheduler").setLevel(logging.WARNING)

def log_user_action(update, text: str):
    user = update.effective_user or update.callback_query.from_user
    username = user.username or user.first_name or "Unknown"
    user_id = user.id
    dialog_logger.info(f"[{user_id}] {username}: {text}")