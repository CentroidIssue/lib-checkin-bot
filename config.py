from dotenv import load_dotenv

import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CRON_JOB_API_KEY = os.getenv("CRON_JOB_API_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
BACKEND_URL = os.getenv("BACKEND_URL")
print(BOT_TOKEN, CRON_JOB_API_KEY, WEBHOOK_URL)