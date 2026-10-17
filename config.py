"""
Jankiz Telegram Bot - Configuration Module
"""

import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env"

if ENV_FILE.exists():
    load_dotenv(ENV_FILE)
else:
    load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
try:
    PORT = int(os.getenv("PORT", "5000"))
except (ValueError, TypeError):
    PORT = 5000
ADMIN_ID = os.getenv("ADMIN_ID", "")
NEWS_UPDATE_INTERVAL = int(os.getenv("NEWS_UPDATE_INTERVAL", "3600")) # 1 hour
