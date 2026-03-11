import os
from dotenv import load_dotenv


load_dotenv()

os.environ("CLIENT_ID")
os.environ("TELEGRAM_BOT_TOKEN")



CLIENT_ID = os.getenv("CLIENT_ID", "DEFAULT")
TOKEN_FILE = "access_token.txt"

SYMBOL = "NSE:NIFTY50-INDEX"
TIMEFRAME_MIN = 10
CANDLE_LIMIT = 40


TIMEZONE = "Asia/Kolkata"


BB_LENGTH = 20
BB_STD = 1
ST_LENGTH = 5
ST_MULTIPLIER = 3


TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN","")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")


