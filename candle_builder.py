from pickletools import read_uint1
import pytz
import pandas as pd
from datetime import date, datetime

from config import TIMEZONE, TIMEFRAME_MIN, SYMBOL
from utils import setup_logger

log = setup_logger(__name__)
IST = pytz.timezone(TIMEZONE)
# datetime.fromtimestamp(ts, tz=IST)

class CandleBuilder:
    def __init__(self, symbol:str = SYMBOL , timeframe_min: int = TIMEFRAME_MIN):
        self.symbol = symbol
        self.timeframe_min = timeframe_min

        self.temp_ltps = []
        self.candle_start = None

        self.candles_df = pd.DataFrame(
            columns=["timestamp","open","high","low","close"]
        )

        log.info(
            "CandleBuilder initialized | symbol=%s | timeframe=%dmin",
            self.symbol, self.timeframe_min
        )

    def add_tick(self, message: dict) -> None:
        ltp = message.get("ltp") # get returns None avoid crsh if key is missing
        ts = message.get("tt")

        if ltp is None or ts is None:
            log.debug("Incomplete tick skipped: %s", message)
            return
        if self.candle_start is None:
            self.candle_start = ts
            log.info(
                "First tick | LTP:%.2f | window opened @ %s IST",
                ltp,
                datetime.fromtimestamp(ts , tz=IST).strftime("%H:%M:%S")
            )
        elapsed = ts - self.candle_start
        window = self.timeframe_min * 60

        if elapsed >= window : 
            self._close_candle(ts)

        self.temp_ltps.append(ltp)


    def _close_candle(self, current_ts: int) -> None:
        if not self.temp_ltps:
            log.warning("Empty window- no ticks collected, skipping candle")


        

