import os
import time
import pandas as pd
import pytz
from datetime import datetime, timedelta
from fyers_apiv3 import fyersModel
 
from config import CLIENT_ID, TIMEZONE , CACHE_DIR , CHUNK_DAYS
from utils import setup_logger, read_access_token
 
log = setup_logger(__name__)
IST = pytz.timezone(TIMEZONE)






def _date_chunks(start : datetime, end : datetime, chunk_days : int = CHUNK_DAYS): # will return list of tuples having chunk satrt and end gap bw them is chunk_days
    chunks = []
    cur= start
    
    while cur < end:
        chunk_end = min(cur + timedelta(days=chunk_days), end)
        chunks.append((cur, chunk_end))
        cur = chunk_end + timedelta(days=1)
    return chunks



def _cache_path(symbol : str , timeframe_min : int , start_date : str , end_date : str) -> str:

    safe_symbol = symbol.replace(":", "_").replace("-", "_")
    filename = f"{safe_symbol}_{timeframe_min}min_{start_date}_{end_date}.csv"
    return os.path.join(CACHE_DIR, filename)



def fetch_backtest_candles(
    symbol : str ,
    timeframe_min : int ,
    start_date : str ,
    end_date :str ,
    use_cache : bool = True,
) -> pd.DataFrame:
    """
    Fetch historical candles for backtesting over an arbitrary date range,
    chunking requests to respect the Fyers API's ~100-day limit per call.
 
    Returns a DataFrame with columns: timestamp, open, high, low, close
    sorted ascending by timestamp, with duplicate timestamps removed.
    """
    os.makedirs(CACHE_DIR, exist_ok=True)
    cache_file = _cache_path(symbol , timeframe_min , start_date , end_date)

    if use_cache and os.path.exists(cache_file):
        log.info("Loading cached data for backtesting %s", cache_file)
        df = pd.read_csv(cache_file , parse_dates = ["timestamp"])
        return df


    access_token = read_access_token()

    fyers =  fyersModel.FyersModel(
        client_id = CLIENT_ID,
        token = access_token,
        log_path = "",

    )
    # a timezone aware datetime object
    start_dt = IST.localize(datetime.strptime(start_date, "%Y-%m-%d"))
    end_dt = IST.localize(datetime.strptime(end_date, "%Y-%m-%d"))
    chunks = _date_chunks(start_dt, end_dt) # list of tuples (start_date, end_date)

    log.info(
        "Fetching backtest data | symbol=%s | tf=%dmin | %s -> %s | %d chunk(s)",
        symbol, timeframe_min, start_date, end_date, len(chunks)
    )


    all_frames = []

    for i, (c_from , c_to) in enumerate(chunks, start=1):
        data = {
            "symbol": symbol,
            "resolution": str(timeframe_min),
            "date_format": "1",
            "range_from": c_from.strftime("%Y-%m-%d"),
            "range_to": c_to.strftime("%Y-%m-%d"),
            "cont_flag": "1",
            } 

       
        log.debug("Chunk %d/%d | %s -> %s", i, len(chunks), data["range_from"], data["range_to"])

        response = fyers.history(data= data)

        if response.get("s")!= "ok":
            raise RuntimeError(f"Fyers API error on chunk {i}: {response}")

        candles = response.get("candles",[])
        if candles:
            chunk_df = pd.DataFrame(
                candles,
                columns = ["timestamp", "open", "high", "low", "close", "volume"]
            )
            all_frames.append(chunk_df)

        if i < len(chunks):
            time.sleep(1)

    if not all_frames:
        raise RuntimeError("No candles returned for the given date range.")

    df = pd.concat(all_frames, ignore_index=True)
    df = df.drop(columns=["volume"])
    df["timestamp"] = df["timestamp"].apply(
        lambda ts: datetime.fromtimestamp(ts, tz=IST)
    )
     # Chunk boundaries can overlap by a candle; drop exact duplicate timestamps.
    df = df.drop_duplicates(subset="timestamp").sort_values("timestamp")
    df = df.reset_index(drop=True)


    log.info(
        "Backtest data ready | count=%d | first=%s | last=%s",
        len(df),
        df["timestamp"].iloc[0].strftime("%d-%b-%Y %H:%M"),
        df["timestamp"].iloc[-1].strftime("%d-%b-%Y %H:%M"),
    )

    df.to_csv(cache_file, index=False)
    log.info("Cached to %s", cache_file)
 
    return df
