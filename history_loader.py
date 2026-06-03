import time
# from numpy import int128
import pandas as pd
import pytz
from datetime import datetime, timedelta
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
    # full_token = f"{CLIENT_ID}:{access_token}"

    fyers = fyersModel.FyersModel(
        client_id=CLIENT_ID,
        token = access_token,
        log_path= "",
    )
    log.info(
    "Fetching %d candles | symbol=%s | timeframe=%d min",
    limit, symbol, timeframe_min)

    range_to = datetime.now(tz=IST)
    range_from = range_to - timedelta(days=7)

    log.debug(
        "Date range | from=%s | to=%s",
        range_from.strftime("%d-%b %H:%M"),
        range_to.strftime("%d-%b %H:%M"),
    )

    data = {
        "symbol" : symbol,
        "resolution" : str(timeframe_min),
        "date_format" : "1",
        "range_from" : range_from.strftime("%Y-%m-%d"),
        "range_to" : range_to.strftime("%Y-%m-%d"),
        "cont_flag" : "1"
    }
    print("sending data",data)
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
    # print(df)
    df2= df.iloc[:-1]
    # df2.tail(50).to_csv("bb_debug.csv", index=False)


    return df2
