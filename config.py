import os
from dotenv import load_dotenv


load_dotenv()




CLIENT_ID = os.getenv("CLIENT_ID", "DEFAULT")
TOKEN_FILE = "access_token.txt"

SYMBOL = "NSE:NIFTY50-INDEX"
TIMEFRAME_MIN = 1
CANDLE_LIMIT = 40


TIMEZONE = "Asia/Kolkata"


BB_LENGTH = 20
BB_STD = 2.0
ST_LENGTH = 5
ST_MULTIPLIER = 3
RSI_LENGTH = 14


TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN","")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")


