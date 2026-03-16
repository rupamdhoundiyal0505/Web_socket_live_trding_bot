import time
from numpy import int128
import pandas as pd
import pytz
from datetime import datetime
from fyers_apiv3 import fyersModel

from config import CLIENT_ID, TIMEZONE, TIMEFRAME_MIN, CANDLE_LIMIT, SYMBOL
from utils import setup_logger, read_access_token

log = setup_logger(__name__)
IST = pytz.timezone(TIMEZONE)

def fetch_historical_candles(
    symbol: str = SYMBOL,
    timeframe_min: int = TIMEFRAME_MIN,
    limit: int = CANDLE_LIMIT,
) -> pd.DataFrame:
    access_token = read_access_token()
    full_token = f"{CLIENT_ID}:{access_token}"

    fyers = fyersModel.FyersModel(
        client_id=CLIENT_ID,
        token = full_token,
        log_path= "",
    )
    log.info(
    "Fetching %d candles | symbol=%s | timeframe=%d min",
    limit, symbol, timeframe_min)

    range_to = int(time.time())
    range_from = range_to - (limit * timeframe_min*60)

    log.debug(
        "Date range | from=%s | to=%s",
        datetime.fromtimestamp(range_from, tz=IST).strftime("%d-%b %H:%M"),
        datetime.fromtimestamp(range_to,   tz=IST).strftime("%d-%b %H:%M"),
    )

    data = {
        "symbol" : symbol,
        "resolution" : str(timeframe_min),
        "date_format" : "1",
        "range_from" : str(range_from),
        "range_to" : str(range_to),
        "cont_flag" : "1"
    }
    response = fyers.history(data=data)
    if response.get("s") != "ok":
        raise RuntimeError(
            f"Fyers API error: {response}"
        )
    log.info("API response recieved | status ok")

    raw_candles = response["candles"]

    df= pd.DataFrame(
        raw_candles,
        columns=["timestamp", "open", "high", "low", "close", "volume"]
        )
    df = df.drop(columns=["volume"])

    df["timestamp"] = df["timestamp"].apply(
        lambda ts : datetime.fromtimestamp(ts, tz=IST)
    )
    df=df.reset_index(drop=True)
    log.info(
        "Candles parsed | count=%d | first=%s | last=%s",
        len(df),
        df["timestamp"].iloc[0].strftime("%d-%b %H:%M"),
        df["timestamp"].iloc[-1].strftime("%d-%b %H:%M"),
    )

    return df
